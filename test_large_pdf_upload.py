#!/usr/bin/env python3
"""
Test the upload and processing of the large PDF that's causing network errors.
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'extractor_project.settings')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files.storage import default_storage
from extractor.models import Vendor, UploadedPDF, ExtractedData
import hashlib
from extractor.tasks import process_pdf_file
import time

def test_large_pdf_upload():
    print("🧪 Testing Large PDF Upload")
    print("=" * 50)
    
    # PDF file path
    pdf_path = r"C:\Users\Mayank\Downloads\MTC-81-150[130322].pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found: {pdf_path}")
        return
    
    # Get file info
    file_size = os.path.getsize(pdf_path)
    size_mb = file_size / (1024 * 1024)
    print(f"📊 File size: {size_mb:.2f} MB ({file_size:,} bytes)")
    
    # Check vendors
    vendors = Vendor.objects.all()
    print(f"📋 Available vendors: {[v.name for v in vendors]}")
    
    if not vendors.exists():
        print("❌ No vendors found in database")
        return
    
    # Use first vendor for test
    vendor = vendors.first()
    print(f"🏭 Using vendor: {vendor.name}")
    
    # Read file and create hash
    print("🔍 Reading file and calculating hash...")
    with open(pdf_path, 'rb') as f:
        file_content = f.read()
    
    file_hash = hashlib.sha256(file_content).hexdigest()
    print(f"🔐 File hash: {file_hash[:16]}...")
    
    # Check for duplicates
    existing = UploadedPDF.objects.filter(file_hash=file_hash).first()
    if existing:
        print(f"⚠️  Duplicate found: {existing.file.name} (uploaded {existing.uploaded_at})")
        print("🧹 Cleaning up for test...")
        # Delete existing data for clean test
        ExtractedData.objects.filter(pdf=existing).delete()
        existing.delete()
    
    try:
        # Test file upload simulation
        print("📤 Simulating file upload...")
        
        # Create uploaded file object
        uploaded_file = SimpleUploadedFile(
            name="MTC-81-150[130322].pdf",
            content=file_content,
            content_type="application/pdf"
        )
        
        # Save file using Django's storage
        filename = f"uploads/{uploaded_file.name}"
        file_path = default_storage.save(filename, uploaded_file)
        print(f"✅ File saved to: {file_path}")
        
        # Create database record
        print("💾 Creating database record...")
        uploaded_pdf = UploadedPDF.objects.create(
            vendor=vendor,
            file=file_path,
            file_hash=file_hash,
            file_size=len(file_content),
            status='PENDING'
        )
        print(f"✅ PDF record created with ID: {uploaded_pdf.id}")
        
        # Test vendor config loading
        print("⚙️  Testing vendor configuration...")
        from extractor.utils.config_loader import find_vendor_config
        from django.conf import settings
        
        vendor_config, config_path = find_vendor_config(vendor, settings)
        if vendor_config:
            print(f"✅ Config loaded from: {config_path}")
            print(f"📋 Config fields: {list(vendor_config.get('fields', {}).keys())}")
        else:
            print(f"❌ Failed to load vendor config")
            return
        
        # Test Celery task (optional - comment out if you don't want to actually process)
        print("🔄 Starting Celery task...")
        task = process_pdf_file.delay(uploaded_pdf.id, vendor_config)
        print(f"✅ Task started with ID: {task.id}")
        
        # Monitor task progress
        print("⏰ Monitoring task progress...")
        start_time = time.time()
        timeout = 300  # 5 minutes timeout for test
        
        while True:
            task.reload()
            elapsed = time.time() - start_time
            
            print(f"   Status: {task.state} (elapsed: {elapsed:.1f}s)")
            
            if task.state == "SUCCESS":
                print("🎉 Task completed successfully!")
                result = task.result
                print(f"📊 Result: {result}")
                break
            elif task.state == "FAILURE":
                print("❌ Task failed!")
                print(f"Error: {task.info}")
                break
            elif elapsed > timeout:
                print("⏰ Task timeout - stopping monitoring")
                break
            
            time.sleep(10)  # Check every 10 seconds
        
        # Check extracted data
        print("\n📋 Checking extracted data...")
        extracted_data = ExtractedData.objects.filter(pdf=uploaded_pdf)
        if extracted_data.exists():
            print(f"✅ Found {extracted_data.count()} extracted records")
            for item in extracted_data[:5]:  # Show first 5
                print(f"   {item.field_key}: {item.field_value}")
        else:
            print("❌ No extracted data found")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n🔧 Current Django Settings:")
    from django.conf import settings
    print(f"   FILE_UPLOAD_MAX_MEMORY_SIZE: {settings.FILE_UPLOAD_MAX_MEMORY_SIZE / (1024*1024):.1f} MB")
    print(f"   DATA_UPLOAD_MAX_MEMORY_SIZE: {settings.DATA_UPLOAD_MAX_MEMORY_SIZE / (1024*1024):.1f} MB")
    if hasattr(settings, 'CELERY_TASK_TIME_LIMIT'):
        print(f"   CELERY_TASK_TIME_LIMIT: {settings.CELERY_TASK_TIME_LIMIT} seconds")

if __name__ == "__main__":
    test_large_pdf_upload()