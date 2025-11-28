#!/usr/bin/env python3
"""
Test script to simulate duplicate file upload scenario
This tests the exact workflow that the user is experiencing.
"""

import os
import sys
import django
import time
import hashlib
from datetime import datetime

# Setup Django
sys.path.append('/code')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'extractor_project.settings')
django.setup()

from django.utils import timezone
from extractor.models import UploadedPDF, Vendor

def test_duplicate_upload_scenario():
    """Test the exact duplicate upload scenario"""
    
    print("🔄 Testing Duplicate Upload Scenario...")
    print("=" * 50)
    
    try:
        vendor = Vendor.objects.first()
        if not vendor:
            print("❌ No vendors found!")
            return
            
        print(f"📊 Using vendor: {vendor.name}")
        
        # Step 1: Create initial PDF
        file_content = b"test file content for duplicate detection"
        file_hash = hashlib.md5(file_content).hexdigest()
        
        original_pdf = UploadedPDF.objects.create(
            file='test_files/duplicate_test.pdf',
            vendor=vendor,
            file_hash=file_hash,
            file_size=len(file_content),
            status='COMPLETED',
            uploaded_at=timezone.now() - timezone.timedelta(hours=1)  # 1 hour ago
        )
        
        print(f"✅ Created original PDF with ID: {original_pdf.id}")
        print(f"📅 Original timestamp: {original_pdf.uploaded_at}")
        print(f"🔗 Hash: {file_hash}")
        
        # Wait a moment
        time.sleep(2)
        
        # Step 2: Simulate duplicate detection and timestamp update (what our fix does)
        print("\n🔄 Simulating duplicate detection...")
        
        # Check for duplicate (like the view does)
        existing_pdfs = UploadedPDF.objects.filter(file_hash=file_hash)
        if existing_pdfs.exists():
            existing_pdf = existing_pdfs.first()
            print(f"📄 Found duplicate PDF ID: {existing_pdf.id}")
            
            # Update timestamp (this is our fix)
            original_timestamp = existing_pdf.uploaded_at
            existing_pdf.uploaded_at = timezone.now()
            existing_pdf.save()
            
            print(f"📅 Updated timestamp from: {original_timestamp}")
            print(f"📅 Updated timestamp to: {existing_pdf.uploaded_at}")
            
            # Test API response
            print(f"\n🔗 Test API call: http://localhost:9000/api/latest-pdfs/")
            print("This should now show the updated PDF with new timestamp")
            
            print("\n📋 Expected behavior:")
            print("1. Dashboard should pick up this PDF as 'new' within 5 seconds")
            print("2. Check browser console for auto-refresh logs")
            print("3. PDF should appear without manual refresh")
            
        # Clean up
        print(f"\nCleaning up test PDF...")
        original_pdf.delete()
        print("🗑️ Test completed")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_duplicate_upload_scenario()