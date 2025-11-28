#!/usr/bin/env python3
"""
Create an improved upload handler for large files with better timeout handling.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'extractor_project.settings')
django.setup()

def create_upload_improvements():
    print("🔧 Creating Upload Improvements for Large Files")
    print("=" * 60)
    
    # 1. Create a custom middleware for large uploads
    middleware_content = '''"""
Custom middleware to handle large file uploads with better error handling.
"""

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger(__name__)

class LargeFileUploadMiddleware(MiddlewareMixin):
    """Middleware to handle large file uploads gracefully"""
    
    def process_exception(self, request, exception):
        """Handle exceptions during file upload"""
        
        # Check if this is a file upload request
        if (request.method == 'POST' and 
            request.content_type and 
            'multipart/form-data' in request.content_type):
            
            # Handle specific upload errors
            if isinstance(exception, (ConnectionError, TimeoutError)):
                logger.error(f"Upload connection error: {exception}")
                return JsonResponse({
                    'error': 'Upload interrupted. Please try again with a smaller file or check your connection.',
                    'type': 'connection_error'
                }, status=408)
            
            elif 'RequestDataTooBig' in str(type(exception)):
                logger.error(f"File too large: {exception}")
                return JsonResponse({
                    'error': 'File is too large. Maximum size is 50MB.',
                    'type': 'file_too_large'
                }, status=413)
        
        return None
'''
    
    # Write middleware
    middleware_path = "extractor/middleware/upload_middleware.py"
    os.makedirs(os.path.dirname(middleware_path), exist_ok=True)
    
    with open(middleware_path, 'w') as f:
        f.write(middleware_content)
    
    print(f"✅ Created: {middleware_path}")
    
    # 2. Create JavaScript improvements for upload progress
    js_improvements = '''
// Enhanced upload handling for large files
function enhanceUploadForm() {
    const uploadForm = document.getElementById('uploadForm');
    const fileInput = document.querySelector('input[type="file"]');
    const progressContainer = document.getElementById('progressContainer');
    const progressBar = document.getElementById('progressBar');
    const progressPhase = document.getElementById('progressPhase');
    const progressPercent = document.getElementById('progressPercent');
    
    if (!uploadForm) return;
    
    // Add file size validation
    fileInput.addEventListener('change', function(e) {
        const file = e.target.files[0];
        if (file) {
            const maxSize = 50 * 1024 * 1024; // 50MB
            const fileSize = file.size;
            const fileSizeMB = (fileSize / (1024 * 1024)).toFixed(2);
            
            console.log(`File selected: ${file.name}, Size: ${fileSizeMB}MB`);
            
            if (fileSize > maxSize) {
                Swal.fire({
                    title: 'File Too Large',
                    text: `File size is ${fileSizeMB}MB. Maximum allowed size is 50MB.`,
                    icon: 'error',
                    confirmButtonText: 'Choose Another File'
                });
                e.target.value = ''; // Clear the file input
                return;
            }
            
            if (fileSize > 10 * 1024 * 1024) { // > 10MB
                Swal.fire({
                    title: 'Large File Detected',
                    text: `This file is ${fileSizeMB}MB. Upload may take longer. Please be patient.`,
                    icon: 'info',
                    confirmButtonText: 'Continue',
                    timer: 3000
                });
            }
        }
    });
    
    // Enhanced form submission with better error handling
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(uploadForm);
        const file = formData.get('pdf');
        
        if (!file || file.size === 0) {
            Swal.fire('Error', 'Please select a PDF file', 'error');
            return;
        }
        
        // Show progress
        progressContainer.style.display = 'block';
        document.querySelector('.upload-container').style.display = 'none';
        
        // Create XMLHttpRequest for upload progress tracking
        const xhr = new XMLHttpRequest();
        let uploadStartTime = Date.now();
        
        // Track upload progress
        xhr.upload.addEventListener('progress', function(e) {
            if (e.lengthComputable) {
                const percentComplete = (e.loaded / e.total) * 100;
                const elapsed = (Date.now() - uploadStartTime) / 1000;
                const speed = e.loaded / elapsed; // bytes per second
                const remaining = (e.total - e.loaded) / speed; // seconds remaining
                
                progressBar.style.width = percentComplete + '%';
                progressPercent.textContent = Math.round(percentComplete) + '%';
                
                if (percentComplete < 100) {
                    progressPhase.innerHTML = `<i class="fas fa-upload"></i> Uploading... (${Math.round(remaining)}s remaining)`;
                } else {
                    progressPhase.innerHTML = `<i class="fas fa-sync-alt fa-spin"></i> Processing...`;
                }
            }
        });
        
        // Handle completion
        xhr.addEventListener('load', function() {
            if (xhr.status === 200) {
                try {
                    const response = JSON.parse(xhr.responseText);
                    if (response.status === 'success') {
                        progressPhase.innerHTML = `<i class="fas fa-check"></i> Upload Complete!`;
                        progressPercent.textContent = '100%';
                        progressBar.style.width = '100%';
                        
                        setTimeout(() => {
                            window.location.href = response.redirect || '/dashboard/';
                        }, 1500);
                    } else {
                        throw new Error(response.error || 'Unknown error');
                    }
                } catch (error) {
                    handleUploadError(error.message);
                }
            } else {
                handleUploadError(`Server error: ${xhr.status}`);
            }
        });
        
        // Handle errors
        xhr.addEventListener('error', function() {
            handleUploadError('Network error during upload. Please check your connection and try again.');
        });
        
        xhr.addEventListener('timeout', function() {
            handleUploadError('Upload timeout. The file may be too large or your connection is slow.');
        });
        
        // Configure request
        xhr.timeout = 300000; // 5 minutes timeout
        xhr.open('POST', uploadForm.action);
        
        // Add CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
        xhr.setRequestHeader('X-CSRFToken', csrfToken);
        
        // Send request
        xhr.send(formData);
    });
    
    function handleUploadError(message) {
        progressContainer.style.display = 'none';
        document.querySelector('.upload-container').style.display = 'block';
        
        Swal.fire({
            title: 'Upload Failed',
            text: message,
            icon: 'error',
            confirmButtonText: 'Try Again',
            footer: 'Tip: Try uploading a smaller file or check your internet connection'
        });
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', enhanceUploadForm);
'''
    
    # Write JavaScript file
    js_path = "extractor/static/extractor/js/large_file_upload.js"
    os.makedirs(os.path.dirname(js_path), exist_ok=True)
    
    with open(js_path, 'w') as f:
        f.write(js_improvements)
    
    print(f"✅ Created: {js_path}")
    
    print(f"\n🔧 Manual Steps Required:")
    print(f"1. Add middleware to settings.py:")
    print(f"   'extractor.middleware.upload_middleware.LargeFileUploadMiddleware',")
    print(f"2. Include JS in upload.html:")
    print(f"   <script src=\"{{% static 'extractor/js/large_file_upload.js' %}}\"></script>")
    print(f"3. Restart Docker containers:")
    print(f"   docker-compose restart web")

if __name__ == "__main__":
    create_upload_improvements()