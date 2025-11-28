from pdf2image import convert_from_path
import pytesseract
import pdfplumber
import re
import logging
from typing import Dict, List, Optional, Union, Tuple
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import numpy as np

# Optional cv2 import for advanced image processing
try:
    import cv2
    # Test if cv2 actually works (some environments have import issues)
    test_array = np.zeros((10, 10), dtype=np.uint8)
    cv2.threshold(test_array, 127, 255, cv2.THRESH_BINARY)
    HAS_CV2 = True
except:
    HAS_CV2 = False

logger = logging.getLogger(__name__)

def preprocess_image_for_ocr(image):
    """
    Preprocess image to improve OCR accuracy for scanned documents.
    
    Args:
        image: PIL Image object
        
    Returns:
        PIL Image: Preprocessed image
    """
    try:
        if HAS_CV2:
            # Advanced preprocessing with OpenCV
            img_array = np.array(image)
            if len(img_array.shape) == 3:
                img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
            else:
                img_cv = img_array
                
            # Convert to grayscale if not already
            if len(img_cv.shape) == 3:
                gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
            else:
                gray = img_cv
                
            # Apply noise reduction
            denoised = cv2.fastNlMeansDenoising(gray)
            
            # Apply adaptive thresholding for better text separation
            adaptive_thresh = cv2.adaptiveThreshold(
                denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply morphological operations to clean up text
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to PIL Image
            processed_pil = Image.fromarray(processed)
        else:
            # Advanced PIL-only preprocessing for better OCR accuracy
            # Convert to grayscale
            processed_pil = image.convert('L')
            
            # Apply aggressive noise reduction using built-in PIL filters
            processed_pil = processed_pil.filter(ImageFilter.MedianFilter(size=3))
            
            # Apply multiple enhancement passes for scanned documents
            # First pass: moderate enhancement
            enhancer = ImageEnhance.Contrast(processed_pil)
            processed_pil = enhancer.enhance(1.8)
            
            # Apply sharpening
            processed_pil = processed_pil.filter(ImageFilter.SHARPEN)
            
            # Second pass: aggressive enhancement for poor scans
            enhancer = ImageEnhance.Contrast(processed_pil)
            processed_pil = enhancer.enhance(1.5)
            
            # Final sharpening
            processed_pil = processed_pil.filter(ImageFilter.UnsharpMask(radius=2, percent=150, threshold=3))
            
        # Additional PIL-based enhancements for both OpenCV and PIL-only paths
        # Increase brightness for dark scans
        enhancer = ImageEnhance.Brightness(processed_pil)
        processed_pil = enhancer.enhance(1.3)
        
        # Final contrast boost
        enhancer = ImageEnhance.Contrast(processed_pil)
        processed_pil = enhancer.enhance(1.4)
        
        # Apply edge enhancement for better text recognition
        processed_pil = processed_pil.filter(ImageFilter.EDGE_ENHANCE_MORE)
        
        return processed_pil
        
    except Exception as e:
        logger.warning(f"Image preprocessing failed, using original: {e}")
        return image.convert('L') if image.mode != 'L' else image

def extract_text_with_ocr(pdf_path, page_num, multilingual=True):
    """
    Extract text from PDF page using OCR with enhanced preprocessing for better accuracy.
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number (0-indexed)
        multilingual: Whether to use multilingual OCR settings
    
    Returns:
        str: Extracted text
    """
    try:
        # Try multiple DPI settings for best results
        dpi_settings = [600, 500, 400, 300]  # Higher DPI first for scanned docs
        images = None
        
        for dpi in dpi_settings:
            try:
                images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1, dpi=dpi)
                if images:
                    logger.debug(f"Successfully converted PDF at {dpi} DPI")
                    break
            except Exception as e:
                logger.debug(f"DPI {dpi} failed: {e}")
                continue
        if not images:
            return ""
        
        original_image = images[0]
        
        # Try multiple preprocessing approaches, including aggressive methods for poor scans
        preprocessing_methods = [
            ("aggressive_enhanced", lambda img: aggressive_preprocess_for_poor_scans(img)),
            ("enhanced", lambda img: preprocess_image_for_ocr(img)),
            ("high_contrast", lambda img: ImageEnhance.Contrast(img.convert('L')).enhance(3.5)),
            ("binary_threshold", lambda img: binarize_image(img)),
            ("contrast_boost", lambda img: ImageEnhance.Contrast(img.convert('L')).enhance(2.0)),
            ("sharpened", lambda img: img.convert('L').filter(ImageFilter.SHARPEN)),
            ("original", lambda img: img.convert('L'))
        ]
        
        best_text = ""
        max_score = 0
        
        for method_name, preprocess_func in preprocessing_methods:
            try:
                processed_image = preprocess_func(original_image)
                
                if multilingual:
                    # Enhanced OCR configurations for different document types
                    ocr_configs = [
                        # For certificates and formal documents
                        {
                            'lang': 'eng',
                            'config': r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-/:()[]{}.,\n\r\t '
                        },
                        # For tables and structured data
                        {
                            'lang': 'eng',
                            'config': r'--oem 3 --psm 4 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-/:()[]{}.,\n\r\t '
                        },
                        # For single text blocks
                        {
                            'lang': 'eng',
                            'config': r'--oem 3 --psm 8 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-/:()[]{}.,\n\r\t '
                        },
                        # Multilingual fallback
                        {
                            'lang': 'eng+chi_sim+kor',
                            'config': r'--oem 3 --psm 6'
                        },
                        # Basic fallback
                        {
                            'lang': 'eng',
                            'config': r'--oem 3 --psm 6'
                        }
                    ]
                    
                    for config in ocr_configs:
                        try:
                            text = pytesseract.image_to_string(
                                processed_image, 
                                lang=config['lang'], 
                                config=config['config']
                            )
                            
                            # Score the result based on content quality
                            score = calculate_text_quality_score(text)
                            
                            if score > max_score:
                                max_score = score
                                best_text = text
                                logger.debug(f"Best OCR result from {method_name} with {config['lang']}: score={score}")
                                
                        except Exception as e:
                            logger.debug(f"OCR config failed: {e}")
                            continue
                            
                else:
                    # Enhanced English-only OCR
                    configs = [
                        r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-/:()[]{}.,\n\r\t ',
                        r'--oem 3 --psm 4',
                        r'--oem 3 --psm 6'
                    ]
                    
                    for config in configs:
                        try:
                            text = pytesseract.image_to_string(processed_image, config=config)
                            score = calculate_text_quality_score(text)
                            
                            if score > max_score:
                                max_score = score
                                best_text = text
                                
                        except Exception as e:
                            logger.debug(f"OCR config failed: {e}")
                            continue
                            
            except Exception as e:
                logger.debug(f"Preprocessing method {method_name} failed: {e}")
                continue
        
        return best_text if best_text else ""
            
    except Exception as e:
        logger.error(f"OCR extraction failed for page {page_num} in {pdf_path}: {e}")
        return ""

def calculate_text_quality_score(text):
    """
    Calculate a quality score for OCR text based on various factors.
    
    Args:
        text: OCR extracted text
        
    Returns:
        float: Quality score (higher is better)
    """
    if not text or not text.strip():
        return 0
    
    score = 0
    
    # Base score from text length
    score += len(text.strip()) * 0.1
    
    # Bonus for alphanumeric characters (good OCR usually has these)
    alphanumeric_chars = sum(1 for c in text if c.isalnum())
    score += alphanumeric_chars * 0.5
    
    # Bonus for common certificate patterns (POSCO-like patterns)
    certificate_patterns = [
        r'[A-Z]{2,3}[-\s]*\d{2,6}',  # Pattern like "SU 123456" or "PP-12345"
        r'\d{4,8}[-\s]*\d{2,4}',     # Pattern like "12345-67" or "123456 78"
        r'[A-Z]+\d+',                # Pattern like "CERT123" or "NO456"
        r'\d+\.\d+',                 # Decimal numbers
        r'\b[A-Z]{2,}\b',            # Uppercase words (often field names)
    ]
    
    for pattern in certificate_patterns:
        matches = len(re.findall(pattern, text))
        score += matches * 2
    
    # Penalty for excessive special characters (often OCR noise)
    special_chars = sum(1 for c in text if not c.isalnum() and c not in ' \n\r\t.,:-()[]{}/')
    score -= special_chars * 0.1
    
    # Bonus for reasonable line structure
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    if 3 <= len(lines) <= 50:  # Reasonable number of lines
        score += 5
    
    return max(0, score)

def binarize_image(image):
    """
    Convert image to pure black and white using optimal thresholding.
    """
    try:
        # Convert to grayscale
        gray_img = image.convert('L')
        
        # Convert to numpy array for processing
        img_array = np.array(gray_img)
        
        # Calculate optimal threshold using Otsu's method approximation
        histogram = np.histogram(img_array, bins=256, range=(0, 256))[0]
        
        # Simple threshold - find the valley between peaks
        threshold = 128  # default
        
        # Find a good threshold by looking for the minimum in the middle range
        middle_range = histogram[64:192]  # Focus on middle gray values
        if len(middle_range) > 0:
            min_idx = np.argmin(middle_range)
            threshold = min_idx + 64
        
        # Apply threshold
        binary_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
        
        return Image.fromarray(binary_array)
        
    except Exception as e:
        logger.debug(f"Binarization failed: {e}")
        return image.convert('L')

def aggressive_preprocess_for_poor_scans(image):
    """
    Aggressive preprocessing for extremely poor quality scanned documents.
    """
    try:
        # Start with grayscale
        processed = image.convert('L')
        
        # Step 1: Extreme contrast enhancement
        enhancer = ImageEnhance.Contrast(processed)
        processed = enhancer.enhance(4.0)
        
        # Step 2: Brightness adjustment to handle dark scans
        enhancer = ImageEnhance.Brightness(processed)
        processed = enhancer.enhance(1.5)
        
        # Step 3: Apply binarization
        processed = binarize_image(processed)
        
        # Step 4: Noise reduction with median filter
        processed = processed.filter(ImageFilter.MedianFilter(size=3))
        
        # Step 5: Morphological operations using PIL filters
        # Erosion approximation (removes noise)
        processed = processed.filter(ImageFilter.MinFilter(3))
        
        # Dilation approximation (restores text)
        processed = processed.filter(ImageFilter.MaxFilter(3))
        
        # Step 6: Final sharpening
        processed = processed.filter(ImageFilter.UnsharpMask(radius=1, percent=200, threshold=2))
        
        return processed
        
    except Exception as e:
        logger.debug(f"Aggressive preprocessing failed: {e}")
        return image.convert('L')

def extract_tabular_data(pdf_path: str, page_num: int) -> Tuple[List[Dict[str, str]], str]:
    """
    Extract tabular data from a PDF page using pdfplumber.
    Also returns raw text for fallback pattern matching.
    
    Args:
        pdf_path: Path to the PDF file
        page_num: Page number (0-indexed)
    
    Returns:
        Tuple containing:
        - List of dictionaries with column headers as keys and cell values as values
        - Raw text from the page for fallback pattern matching
    """
    try:
        with pdfplumber.open(pdf_path) as pdf:
            page = pdf.pages[page_num]
            
            # Extract raw text for fallback
            raw_text = page.extract_text()
            
            # Extract tables from the page
            tables = page.extract_tables()
            if not tables:
                return [], raw_text
                
            # Process all tables found on the page
            results = []
            for table in tables:
                # Skip empty tables
                if not table or not any(table):
                    continue
                    
                # Try to find header row
                header_row = table[0]
                if not header_row or not any(header_row):
                    continue
                    
                # Clean and normalize headers
                headers = [str(h).strip() if h else f"column_{i}" 
                          for i, h in enumerate(header_row)]
                
                # Process each data row
                for row in table[1:]:
                    if not row or not any(row):
                        continue
                        
                    # Create dictionary mapping headers to cell values
                    row_dict = {}
                    for header, cell in zip(headers, row):
                        if cell:
                            row_dict[header] = str(cell).strip()
                    
                    if row_dict:  # Only add non-empty rows
                        results.append(row_dict)
            
            return results, raw_text
            
    except Exception as e:
        logger.error(f"Table extraction failed for page {page_num} in {pdf_path}: {e}")
        return [], ""

def extract_pattern_matches(text: str, pattern: str, match_type: str = "line_by_line") -> List[str]:
    """
    Extract all pattern matches from text using specified matching strategy.
    
    Args:
        text: Text to search for patterns
        pattern: Regular expression pattern
        match_type: Matching strategy - "line_by_line" or "global"
    
    Returns:
        List of matched values
    """
    matches = []
    try:
        if match_type == "line_by_line":
            # Split text into lines and search each line
            lines = text.split('\n')
            for line in lines:
                line_matches = re.finditer(pattern, line)
                for match in line_matches:
                    if match.groups():
                        matches.append(match.group(1))  # Capture first group
                    else:
                        matches.append(match.group(0))  # Or full match
        else:  # global matching
            # Search entire text at once
            text_matches = re.finditer(pattern, text)
            for match in text_matches:
                if match.groups():
                    matches.append(match.group(1))
                else:
                    matches.append(match.group(0))
                    
    except Exception as e:
        logger.error(f"Pattern matching failed for pattern {pattern}: {e}")
    
    return list(set(matches))  # Remove duplicates
