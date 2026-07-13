Project Title
*ForensiVault* - Digital Evidence Management and Chain of Custody System
Team Members
• Kashika Nanda
Project Description
This project is a secure digital evidence management system built with Python, Streamlit, and SQLite. It supports case management, evidence registration, SHA-256 integrity verification, encryption, chain of custody tracking, tamper alerts, RBAC, activity monitoring, and report generation.
Software Requirements
Operating System: Windows 10/11
Python: 3.10+
Framework: Streamlit
Database: SQLite
IDE: Visual Studio Code

Packages:
streamlit
pandas
bcrypt
cryptography
Pillow
PyPDF2
matplotlib
plotly
reportlab
Installation Steps
1. Extract the project.
2. Open it in VS Code.
3. Create a virtual environment:
   python -m venv .venv
4. Activate it:
   .venv\Scripts\activate
5. Install packages:
   pip install streamlit pandas bcrypt cryptography pillow PyPDF2 matplotlib plotly reportlab
Database Import Steps
Option 1: Delete any old forensic.db and run the application once. The init_db() function creates all tables automatically.

Option 2: Place the provided forensic.db file in the project root beside app.py.
Execution Instructions
1. Activate the virtual environment.
2. Navigate to the project folder.
3. Run:
   streamlit run app.py
4. Open the displayed localhost URL.
5. Log in as Administrator or register a Viewer account.
6. Use the application modules from the dashboard.
