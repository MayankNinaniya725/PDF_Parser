#!/usr/bin/env python3
"""
Analyze the problematic PDF file to understand why network errors occur.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'extractor_project.settings')
django.setup()

def analyze_pdf():
    print("🔍 Analyzing PDF Upload Issue")
    print("=" * 50)
    
    # PDF file paths to check
    pdf_paths = [
        r"C:\Users\Mayank\Downloads\MTC-81-150[130322].pdf",
        r"C:\Users\Mayank\Downloads\OneDrive_1_18-9-2025\MTC-81-150[130322].pdf"
    ]
    
    for pdf_path in pdf_paths:
        print(f"\n📁 Checking: {pdf_path}")
        
        if not os.path.exists(pdf_path):
            print(f"   ❌ File not found")
            continue
            
        # Get file size
        file_size = os.path.getsize(pdf_path)
        size_mb = file_size / (1024 * 1024)
        
        print(f"   📊 File size: {file_size:,} bytes ({size_mb:.2f} MB)")
        
        # Check if file size might cause issues
        if size_mb > 50:
            print(f"   ⚠️  Large file detected - may cause timeout issues")
        elif size_mb > 20:
            print(f"   ⚠️  Medium file - may need longer processing time")
        else:
            print(f"   ✅ Normal file size")
        
        # Try to analyze PDF structure
        try:
            import pdfplumber
            
            with pdfplumber.open(pdf_path) as pdf:
                num_pages = len(pdf.pages)
                print(f"   📄 Pages: {num_pages}")
                
                if num_pages > 20:
                    print(f"   ⚠️  Many pages detected - may cause processing timeout")
                elif num_pages > 10:
                    print(f"   ⚠️  Moderate page count - processing may take longer")
                else:
                    print(f"   ✅ Normal page count")
                
                # Check first page for content
                if num_pages > 0:
                    first_page = pdf.pages[0]
                    text_sample = first_page.extract_text()
                    text_length = len(text_sample) if text_sample else 0
                    
                    print(f"   📝 First page text length: {text_length} characters")
                    
                    if text_length == 0:
                        print(f"   ⚠️  No text found - may be scanned image requiring OCR")
                    else:
                        print(f"   ✅ Text content detected")
                        
        except Exception as e:
            print(f"   ❌ Error analyzing PDF: {e}")
    
    # Check current Django settings that might affect uploads
    print(f"\n🔧 Django Configuration Check:")
    
    from django.conf import settings
    
    # Check file upload limits
    if hasattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE'):
        max_memory = settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024 * 1024)
        print(f"   📤 Max memory upload: {max_memory:.1f} MB")
    
    if hasattr(settings, 'DATA_UPLOAD_MAX_MEMORY_SIZE'):
        max_data = settings.DATA_UPLOAD_MAX_MEMORY_SIZE / (1024 * 1024)
        print(f"   📊 Max data upload: {max_data:.1f} MB")
    
    # Check Celery task timeout
    if hasattr(settings, 'CELERY_TASK_TIME_LIMIT'):
        timeout = settings.CELERY_TASK_TIME_LIMIT
        print(f"   ⏰ Celery timeout: {timeout} seconds")
    else:
        print(f"   ⚠️  No Celery timeout configured")
    
    print(f"\n💡 Recommendations:")
    print(f"   1. Check file size limits in Django settings")
    print(f"   2. Increase Celery task timeout for large files")
    print(f"   3. Add progress tracking for long-running tasks")
    print(f"   4. Consider chunked upload for large files")
    print(f"   5. Check web server (nginx/apache) upload limits")
    print(f"   6. Monitor server memory usage during upload")

if __name__ == "__main__":
    analyze_pdf()