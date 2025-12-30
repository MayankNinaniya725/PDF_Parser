import os
import sys
import django
import argparse
import json
from extractor.utils.extractor import extract_pdf_fields

def setup_django():
    """Sets up the Django environment to allow access to models."""
    # The path to the project's root directory.
    # Assuming the script is in the project root.
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.append(project_root)
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'extractor_project.settings')
    django.setup()

def run_extraction_test(pdf_path, vendor_name):
    """
    Runs a test of the PDF extraction process for a given PDF file and vendor.
    """
    print(f"--- Running Extraction Test ---")
    print(f"PDF File: {pdf_path}")
    print(f"Vendor: {vendor_name}")
    print("---------------------------------")

    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found at '{pdf_path}'")
        return

    setup_django()

    from extractor.models import Vendor

    try:
        vendor = Vendor.objects.get(name__iexact=vendor_name)
        
        if not vendor.config_file:
            print(f"Error: No configuration file found for vendor '{vendor_name}'.")
            return

        from django.conf import settings
        config_path = os.path.join(settings.MEDIA_ROOT, vendor.config_file.name)
        
        if not os.path.exists(config_path):
             print(f"Error: Configuration file not found at '{config_path}'. Looking in alternative path.")
             # Alternative path based on create_vendor_templates.py
             config_path = os.path.join(settings.BASE_DIR, 'extractor', 'vendor_configs', os.path.basename(vendor.config_file.name))
             if not os.path.exists(config_path):
                 print(f"Error: Configuration file not found at '{config_path}' either.")
                 return


        with open(config_path, 'r') as f:
            vendor_config = json.load(f)

        if not vendor_config:
            print(f"Error: Could not load configuration for vendor '{vendor_name}'.")
            return
    except Vendor.DoesNotExist:
        print(f"Error: Vendor '{vendor_name}' not found in the database.")
        return
    except Exception as e:
        print(f"An error occurred while loading vendor configuration: {e}")
        return

    print("Vendor configuration loaded successfully.")

    try:
        results, stats = extract_pdf_fields(pdf_path, vendor_config)

        print("\n--- Extraction Results ---")
        if results:
            for entry in results:
                plate_no = entry.get("PLATE_NO", "NA")
                heat_no = entry.get("HEAT_NO", "NA")
                cert_no = entry.get("TEST_CERT_NO", "NA")
                print(f"PLATE_NO: {plate_no}, HEAT_NO: {heat_no}, TEST_CERT_NO: {cert_no}")
        else:
            print("No data extracted.")

        print("\n--- Extraction Stats ---")
        print(json.dumps(stats, indent=2))
        print("--------------------------")

    except Exception as e:
        print(f"\nAn error occurred during PDF extraction: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run a PDF extraction test.")
    parser.add_argument("pdf_path", type=str, help="The full path to the PDF file to test.")
    parser.add_argument("vendor_name", type=str, help="The name of the vendor to use for extraction.")
    args = parser.parse_args()

    run_extraction_test(args.pdf_path, args.vendor_name)
