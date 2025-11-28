
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
