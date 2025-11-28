from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import RedirectView
from django.shortcuts import render
from . import views
from .views.core import process_pdf, dashboard, upload_pdf, task_progress
from .views.auth import login_view, logout_view
from .views.downloads import download_all_pdfs_package
from .views.download_views import download_package, download_large_package
from .views.single_file_package import download_single_file_package, download_individual_pdf
from .views.pdf_package_views import download_package_by_filename, download_package_by_pdf_id
from .views.api_views import get_extracted_files_status, list_all_extracted_directories, get_latest_pdfs


urlpatterns = [
    # Redirect root to upload page
    path('', RedirectView.as_view(url='/upload/'), name='root'),
    
    # Auth URLs
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    # PDF processing URLs
    path('process-pdf/', process_pdf, name='process_pdf'),
    
    # Core URLs - dashboard and upload are public
    path('dashboard/', dashboard, name='dashboard'),
    path('upload/', upload_pdf, name='upload_pdf'),

    # Progress tracking - public (needed for upload process)
    path('task-status/<str:task_id>/', views.task_status, name='task_status'),
    path('progress/<str:task_id>/', task_progress, name='task_progress'),
    # Download endpoints - public (no login required)
    path('download/single-file-package/<str:pdf_id>/', download_single_file_package, name='download_single_file_package'),
    path('download/individual-pdf/<str:pdf_id>/', download_individual_pdf, name='download_individual_pdf'),
    path('download/excel/', views.download_excel, name='download_excel'),
    path('download/pdfs-with-excel/', views.download_pdfs_with_excel, name='download_pdfs_with_excel'),
    path('download/all-pdfs-package/', download_all_pdfs_package, name='download_all_pdfs_package'),
    path('download/package/', download_package, name='download_package'),
    path('download/large-package/', download_large_package, name='download_large_package'),
    path('download/pdf-package/', download_package_by_filename, name='download_pdf_package'),
    path('download/pdf-package/<int:pdf_id>/', download_package_by_pdf_id, name='download_pdf_package_by_id'),
    
    # New API endpoint for downloading packages by file_id  
    path('download/package/<int:file_id>/', views.download_package_api, name='download_package_by_file_id'),
    
    # API endpoints - public (for dashboard functionality)
    path('api/extracted-files-status/', get_extracted_files_status, name='api_extracted_files_status'),
    path('api/extraction-directories/', list_all_extracted_directories, name='api_extraction_directories'),
    path('api/latest-pdfs/', get_latest_pdfs, name='api_latest_pdfs'),
    
    # Test page for API debugging
    path('test-api/', lambda request: render(request, 'test_api.html'), name='test_api'),
    path('test-upload-refresh/', lambda request: render(request, 'test_upload_refresh.html'), name='test_upload_refresh'),
    
    # Admin-only functions
    path('regenerate-excel/', login_required(views.regenerate_excel), name='regenerate_excel'),
]
