"""
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
