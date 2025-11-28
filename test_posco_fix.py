#!/usr/bin/env python3
"""
Quick test to verify POSCO extraction fix is working
"""
import os
import sys
import django
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'extractor_project.settings')
django.setup()

from extractor.utils.config_loader import load_vendor_config

def test_posco_fix():
    """Test that POSCO extraction fix is properly loaded"""
    print("🔍 Testing POSCO Extraction Fix")
    print("=" * 40)
    
    # 1. Test config loading
    try:
        config = load_vendor_config('extractor/vendor_configs/posco_steel.json')
        print(f"✅ Config loaded successfully")
        print(f"   - Vendor ID: {config['vendor_id']}")
        print(f"   - Vendor Name: {config['vendor_name']}")
        print(f"   - Extraction Mode: {config['extraction_mode']}")
    except Exception as e:
        print(f"❌ Config loading failed: {e}")
        return False
    
    # 2. Test POSCO parser import
    try:
        from extractor.utils.posco_table_parser import extract_posco_table_data
        print("✅ POSCO specialized parser imported successfully")
    except Exception as e:
        print(f"❌ POSCO parser import failed: {e}")
        return False
    
    # 3. Test extractor logic
    try:
        from extractor.utils.extractor import extract_pdf_fields
        print("✅ Main extractor function imported successfully")
        
        # Check if the POSCO logic is uncommented
        import inspect
        source = inspect.getsource(extract_pdf_fields)
        if "Using POSCO specialized table parser" in source and "# Re-enabled specialized POSCO parser" in source:
            print("✅ POSCO specialized parser is ENABLED in extraction logic")
        else:
            print("❌ POSCO specialized parser appears to be DISABLED")
            return False
            
    except Exception as e:
        print(f"❌ Extractor import failed: {e}")
        return False
    
    # 4. Test vendor detection
    vendor_id = config['vendor_id']
    vendor_name = config['vendor_name']
    
    posco_check1 = vendor_id.lower() == "posco"
    posco_check2 = "posco" in vendor_name.lower()
    
    print(f"\n🎯 Vendor Detection Test:")
    print(f"   - vendor_id == 'posco': {posco_check1}")
    print(f"   - 'posco' in vendor_name: {posco_check2}")
    print(f"   - Overall POSCO detection: {posco_check1 or posco_check2}")
    
    if posco_check1 or posco_check2:
        print("✅ POSCO vendor detection will work correctly")
    else:
        print("❌ POSCO vendor detection may fail")
        return False
    
    print("\n🎉 All POSCO extraction fixes are properly loaded!")
    print("\n📋 Next Steps:")
    print("   1. Go to http://localhost:8000")
    print("   2. Upload your MTC-81-150[130322].pdf file")
    print("   3. Select 'posco_steel' as vendor")
    print("   4. Verify multiple entries are extracted (not OCR fallback)")
    
    return True

if __name__ == "__main__":
    test_posco_fix()