import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'extractor_project.settings')
django.setup()

from extractor.models import Vendor

def list_vendors():
    print("--- Available Vendors ---")
    try:
        vendors = Vendor.objects.all()
        if vendors.exists():
            for vendor in vendors:
                print(f"- {vendor.name}")
        else:
            print("No vendors found in the database.")
    except Exception as e:
        print(f"An error occurred while fetching vendors: {e}")
    print("-------------------------")

if __name__ == "__main__":
    list_vendors()
