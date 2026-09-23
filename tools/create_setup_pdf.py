from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, Preformatted, SimpleDocTemplate, Spacer


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_ROOT / "SLOPESHIELD_NER_SETUP_GUIDE.pdf"


def build_pdf():
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "GuideTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        leading=28,
        spaceAfter=8,
    )
    subtitle = ParagraphStyle(
        "GuideSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor="#555555",
        spaceAfter=18,
    )
    body = ParagraphStyle(
        "GuideBody",
        parent=styles["BodyText"],
        fontSize=9.5,
        leading=14,
        spaceAfter=7,
    )
    heading = ParagraphStyle(
        "GuideHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=9,
        spaceAfter=7,
        textColor="#17324d",
    )
    code = ParagraphStyle(
        "GuideCode",
        parent=styles["Code"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        leftIndent=8,
        rightIndent=8,
        spaceBefore=4,
        spaceAfter=8,
        backColor="#f1f4f6",
    )

    document = SimpleDocTemplate(
        str(OUTPUT_PATH),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="SLOPESHIELD NER Setup Guide",
        author="SLOPESHIELD NER",
    )

    story = [
        Paragraph("SLOPESHIELD NER", title),
        Paragraph("Setup guide for running the complete website on another Windows laptop", subtitle),
        Paragraph("What this guide is for", heading),
        Paragraph("Use this guide to run the complete SLOPESHIELD NER frontend and backend after copying the full project folder.", body),
        Paragraph("Required software", heading),
        Paragraph("- Windows 10 or Windows 11<br/>- Node.js 20 LTS or newer: https://nodejs.org/<br/>- Python 3.11 or newer: https://www.python.org/downloads/<br/>- Internet connection for the first setup", body),
        Paragraph("During Python installation, enable <b>Add Python to PATH</b>. Docker Desktop is optional; without Docker, the application uses local SQLite.", body),
        Paragraph("Files to transfer", heading),
        Paragraph("Copy the complete SLOPESHIELD_NER_Project folder. Do not remove the backend, src, public, package.json, requirements.txt, or run_SLOPESHIELD.bat files. Generated folders such as node_modules and backend/.venv do not need to be copied.", body),
        Paragraph("Recommended startup", heading),
        Paragraph("1. Install Node.js and Python.<br/>2. Extract or copy the project folder.<br/>3. Double-click run_SLOPESHIELD.bat.<br/>4. Wait for first-run dependency installation.<br/>5. Open http://127.0.0.1:5173.", body),
        Paragraph("Services started by the launcher", heading),
        Paragraph("Frontend: http://127.0.0.1:5173<br/>Backend: http://127.0.0.1:8000<br/>API documentation: http://127.0.0.1:8000/docs", body),
        Paragraph("Keep the API and frontend command windows open while using the website.", body),
        PageBreak(),
        Paragraph("Manual startup", title),
        Paragraph("Run these commands once from the project folder:", body),
        Preformatted('npm install\npy -3 -m venv backend\\.venv\nbackend\\.venv\\Scripts\\python.exe -m pip install -r backend\\requirements.txt\ncopy backend\\.env.example backend\\.env', code),
        Paragraph("Backend window", heading),
        Preformatted('cd "C:\\path\\to\\SLOPESHIELD_NER_Project"\nbackend\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000', code),
        Paragraph("Frontend window", heading),
        Preformatted('cd "C:\\path\\to\\SLOPESHIELD_NER_Project"\nnpm run dev -- --host 127.0.0.1', code),
        Paragraph("Troubleshooting", heading),
        Paragraph("Node.js or npm is missing: install Node.js 20 LTS or newer, reopen PowerShell, and run the launcher again.<br/><br/>Python is missing: install Python 3.11 or newer with Add Python to PATH enabled, reopen PowerShell, and run the launcher again.<br/><br/>The website says the API is not running: keep the SLOPESHIELD API window open and check http://127.0.0.1:8000/health.<br/><br/>Port 5173 or 8000 is already in use: close the application using that port and run the launcher again.<br/><br/>Docker is not installed: no action is required; SQLite is used automatically.", body),
        Paragraph("Stopping the application", heading),
        Paragraph("Close the frontend and API command windows. If Docker was used, run:", body),
        Preformatted('docker compose -f backend\\docker-compose.yml down', code),
    ]

    document.build(story)
    print(OUTPUT_PATH)


if __name__ == "__main__":
    build_pdf()