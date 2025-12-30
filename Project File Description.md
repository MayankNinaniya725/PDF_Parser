# Project File Description

### **Project Overview**

This project appears to be a **PDF Data Extraction System**. It is a web-based application, likely built using the **Django** framework in Python, designed to automate the process of extracting structured data from PDF documents. The system seems to handle different PDF layouts from various "vendors" (e.g., Hengrun, Posco, Iraeta), uses Optical Character Recognition (OCR) for text extraction, and provides a dashboard for users to view and manage the extracted data.

The project is containerized using **Docker**, which allows for consistent deployment across different environments. It also includes a variety of scripts for database management, debugging, testing, and data analysis, indicating a complex and mature system.

---

### **Root Directory: File Explanations**

This section explains the files located in the main project folder.

#### **Configuration and Environment Files**

These files are crucial for setting up the development and production environments.

*   **File:** `requirements.txt`
    *   **File Type:** Text (Configuration)
    *   **Purpose:** Lists all the Python libraries and packages required for the project to run.
    *   **Functionality:** It is used by `pip` (Python's package installer) to install all dependencies, ensuring a consistent environment. For example, `pip install -r requirements.txt`.
    *   **Interaction:** Interacts with the Python environment.
    *   **Relation:** Core configuration file.
    *   **Libraries:** Specifies versions for frameworks like Django, Celery, and other data processing libraries.

*   **File:** `.env.local` / `.env.docker`
    *   **File Type:** Environment Configuration
    *   **Purpose:** To store environment variables for local and Docker-based setups, respectively.
    *   **Functionality:** These files hold sensitive information like database credentials, secret keys, and API keys, keeping them separate from the source code. The application reads these files at startup to configure itself.
    *   **Interaction:** Read by the Django settings file (`extractor_project/settings.py`) to load configuration values.
    *   **Relation:** Configuration.

#### **Docker Files**

These files are used to build and run the application inside Docker containers, ensuring portability and scalability.

*   **File:** `Dockerfile`
    *   **File Type:** Docker Configuration
    *   **Purpose:** Contains a set of instructions to build a Docker image for the application.
    *   **Functionality:** It defines the base image (e.g., a Python image), copies the project files into the image, installs the dependencies from `requirements.txt`, and specifies the command to run the application.
    *   **Interaction:** Used by the `docker build` command.
    *   **Relation:** Core configuration for deployment.

*   **File:** `docker-compose.yml`
    *   **File Type:** Docker Compose Configuration
    *   **Purpose:** To define and run a multi-container Docker application.
    *   **Functionality:** This file likely defines services for the web application (Django), a database (like PostgreSQL), a message broker (like Redis for Celery), and a Celery worker for background tasks. It orchestrates the startup and networking of these containers.
    *   **Interaction:** Used by the `docker-compose up` command.
    *   **Relation:** Core configuration for deployment.

#### **Django Core Files**

These are the central files for the Django web framework.

*   **File:** `manage.py`
    *   **File Type:** Python Script
    *   **Purpose:** Django's command-line utility for administrative tasks.
    *   **Functionality:** It's a thin wrapper around `django-admin`. It is used to run development servers, create database migrations, run tests, and other management tasks. For example, `python manage.py runserver`.
    *   **Interaction:** It is the primary entry point for interacting with the Django project from the command line. It uses the settings in `extractor_project/settings.py`.
    *   **Relation:** Core.

#### **Database Files**

These files store the application's data.

*   **File:** `db.sqlite3`
    *   **File Type:** SQLite Database
    *   **Purpose:** The default database for a new Django project. It stores all application data, such as user information and extracted PDF data.
    *   **Functionality:** This is a lightweight, file-based database, suitable for development and small-scale applications.
    *   **Relation:** Data storage.

*   **Files:** `extractor_backup.sql`, `extractor_db.sql`, `mydb.sql`
    *   **File Type:** SQL Scripts
    *   **Purpose:** These are likely SQL dump files used for backing up or restoring the database. They contain the SQL commands to recreate the database schema and its data.
    *   **Relation:** Supporting/Backup.

#### **Scripts (Python, PowerShell, Shell)**

The project contains a large number of scripts, indicating a focus on automation, testing, and maintenance. They are supporting files, not part of the core web application logic that runs on the server.

*   **General Purpose Scripts:**
    *   `start.sh` / `start.ps1`: Scripts to start the application services, likely running the Django development server and Celery workers.
    *   `run_test.sh` / `run_test.ps1`: Scripts to execute the project's test suite.
    *   `clear_cache.ps1`: A PowerShell script probably used to clear application or system cache during development.

*   **Debugging Scripts (`debug_*.py`):**
    *   These scripts (`debug_hengrun_pdf.py`, `debug_posco_extraction.py`, etc.) are created to diagnose and troubleshoot specific issues with PDF processing for different vendors or functionalities. They are for development and not used in production.

*   **Testing Scripts (`test_*.py`):**
    *   These scripts (`test_complete_flow.py`, `test_extraction.py`, etc.) are used to test specific parts of the application, such as the data extraction flow, API endpoints, or vendor-specific logic.

*   **Data Analysis & Verification Scripts (`analyze_*.py`, `final_verification.py`):**
    *   These scripts (`analyze_posco_pdf.py`, `full_ocr_analysis.py`) are used for one-off analysis tasks, such as evaluating the OCR output or understanding the structure of a new PDF type.

*   **Database & Migration Scripts (`add_*.py`, `fix_*.py`):**
    *   Scripts like `add_status_field.py` and `fix_page_numbers.py` appear to be custom scripts to perform data migrations or corrections in the database, which might be too complex for a standard Django migration.

*   **Vendor & Template Scripts (`create_vendor_templates.py`, `list_vendors.py`):**
    *   These scripts are likely used to manage configurations for different PDF vendors.

#### **Documentation**

*   **File:** `README.md`
    *   **File Type:** Markdown
    *   **Purpose:** The main documentation file for the project. It typically contains an overview of the project, setup instructions, and usage guidelines.
    *   **Relation:** Documentation.

*   **File:** `License.md`
    *   **File Type:** Markdown
    *   **Purpose:** Contains the software license for the project, defining how it can be used and distributed.
    *   **Relation:** Documentation.

---

### **Directory Explanations**

#### **`extractor_project/`**

This is the main Django project package.

*   **`extractor_project/settings.py`**: The heart of the Django configuration. It defines database settings, installed apps, middleware, template locations, and reads from `.env` files.
*   **`extractor_project/urls.py`**: The main URL routing file. It maps URL patterns to different views in the application, directing user requests to the correct logic.
*   **`extractor_project/wsgi.py` / `asgi.py`**: Entry points for WSGI/ASGI-compatible web servers to serve the application in a production environment.
*   **`extractor_project/celery.py`**: Configuration file for Celery, the distributed task queue. It defines how background tasks (like PDF processing) are discovered and managed.

#### **`extractor/`**

This is a Django "app" that likely contains the core logic for the PDF extraction functionality.

*   **`extractor/models.py`**: Defines the database schema using Django's ORM. It would contain classes for `PDFDocument`, `ExtractedData`, `Vendor`, etc.
*   **`extractor/views.py`**: Contains the business logic for handling web requests. This is where PDF uploads are processed, data is displayed, and downloads are initiated.
*   **`extractor/tasks.py`**: Defines the background tasks that are executed by Celery. The main PDF processing and OCR logic would be here to avoid blocking web requests.
*   **`extractor/admin.py`**: Configures the Django admin interface for the models in this app, allowing administrators to manage data directly.
*   **`extractor/urls.py`**: Contains URL routes specific to this app.

#### **`templates/`**

This directory holds the HTML templates for the user interface.

*   **Functionality:** Django's templating engine uses these files to generate the HTML sent to the user's browser. It would contain templates for the upload page, dashboard, data display, and login pages.

#### **`static/`**

This directory stores static assets for the frontend.

*   **Functionality:** It contains CSS files for styling, JavaScript files for client-side interactivity (like dashboard auto-refresh), and images.

#### **`media/`**

This directory is where user-uploaded files are stored.

*   **Functionality:** When a user uploads a PDF, it is saved in this directory for the backend to process.

#### **`logs/`**

This directory contains log files generated by the application.

*   **Functionality:** Logging is crucial for debugging. These files would contain records of application events, errors, and the output of the PDF processing tasks.

---

### **System Workflow (Inferred)**

1.  **Upload:** A user uploads a PDF file through the web interface (defined in `templates/` and handled by a view in `extractor/views.py`).
2.  **Save:** The uploaded PDF is saved to the `media/` directory.
3.  **Task Queuing:** The view then creates a background task to process the PDF and adds it to the Celery queue (using Redis as a broker). This immediately returns a response to the user, so they don't have to wait.
4.  **Background Processing:** A Celery worker picks up the task and executes the logic in `extractor/tasks.py`. This involves:
    *   Running OCR on the PDF to extract text.
    *   Applying vendor-specific patterns to find and parse the required data.
    *   Saving the structured data to the database (using models from `extractor/models.py`).
5.  **Display:** The user can view the extracted data on a dashboard, which fetches the information from the database and displays it using another view and template.

This architecture is robust and scalable, as the heavy lifting of PDF processing is handled by background workers, allowing the web application to remain responsive.
