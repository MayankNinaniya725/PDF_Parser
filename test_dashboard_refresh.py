#!/usr/bin/env python3
"""
Test script to verify dashboard auto-refresh functionality
This script creates a fake PDF entry to test if the dashboard updates automatically.
"""

import os
import sys
import django
import time
from datetime import datetime

# Setup Django
sys.path.append('/code')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'extractor_project.settings')
django.setup()

from django.utils import timezone
from extractor.models import UploadedPDF, Vendor

def test_dashboard_refresh():
    """Test if dashboard auto-refresh picks up new PDFs"""
    
    print("🔄 Testing Dashboard Auto-Refresh...")
    print("=" * 50)
    
    # Get a vendor to use
    try:
        vendor = Vendor.objects.first()
        if not vendor:
            print("❌ No vendors found! Please create a vendor first.")
            return
            
        print(f"📊 Using vendor: {vendor.name}")
        
        # Create a test PDF entry
        test_pdf = UploadedPDF.objects.create(
            file='test_files/test_auto_refresh.pdf',
            vendor=vendor,
            file_hash='test_hash_' + str(int(time.time())),
            file_size=1024,
            status='COMPLETED',
            uploaded_at=timezone.now()
        )
        
        print(f"✅ Created test PDF with ID: {test_pdf.id}")
        print(f"📅 Upload timestamp: {test_pdf.uploaded_at}")
        print(f"🔗 Check dashboard: http://localhost:9000/dashboard/")
        print(f"🔗 Check API: http://localhost:9000/api/latest-pdfs/")
        
        print("\n📋 Instructions:")
        print("1. Open dashboard in browser")
        print("2. Open browser console (F12)")
        print("3. You should see this new PDF appear automatically")
        print("4. Check console logs for auto-refresh activity")
        
        # Wait a moment, then clean up
        print("\nWaiting 30 seconds before cleanup...")
        time.sleep(30)
        
        test_pdf.delete()
        print("🗑️ Test PDF cleaned up")
        
    except Exception as e:
        print(f"❌ Error during test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_dashboard_refresh()