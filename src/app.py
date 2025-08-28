from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
import shutil
import json
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from src.financial_analyzer.utils.analysis import analyze_financials
from src.financial_analyzer.utils.pdf_extractor import save_extracted

import os

os.environ["OPENAI_API_KEY"] = "YOUR API KEY HERE"

app = FastAPI(title="Financial Document Analyzer API")

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

EXTRACTED_JSON = DATA_DIR / "extracted.json"
RESULT_TXT = DATA_DIR / "analysis_result.txt"
RESULT_PDF = DATA_DIR / "analysis_result.pdf"
RESULT_CSV = DATA_DIR / "extracted.csv"
RESULT_XLSX = DATA_DIR / "extracted.xlsx"


def save_results_as_txt(results: str):
    with open(RESULT_TXT, "w", encoding="utf-8") as f:
        f.write(results)


def save_results_as_pdf(results: str):
    doc = SimpleDocTemplate(str(RESULT_PDF), pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    lines = results.split("\n")
    table_data = []
    for line in lines:
        if line.strip():
            table_data.append([Paragraph(line, styles['Normal'])])

    table = Table(table_data, colWidths=[500])
    table.setStyle(
        TableStyle([
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ])
    )

    elements.append(table)
    doc.build(elements)

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Welcome to the Financial Document Analyzer API! Visit /docs for interactive API."}


@app.post("/analyze/")
async def analyze_pdf(file: UploadFile = File(...), company: str = "Unknown", quarter: str = ""):
    if not file.filename.endswith(".pdf"):
        return JSONResponse({"error": "Only PDF files are supported"}, status_code=400)

    # Save uploaded PDF
    pdf_path = DATA_DIR / file.filename
    with open(pdf_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Step 1: Extract PDF
    save_extracted(str(pdf_path), str(EXTRACTED_JSON))

    # Step 2: Convert to CSV & Excel
    with open(EXTRACTED_JSON, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df.to_csv(RESULT_CSV, index=False)
    df.to_excel(RESULT_XLSX, index=False)

    # Step 3: Analyze
    results = analyze_financials(str(EXTRACTED_JSON), company=company, quarter=quarter)

    # Step 4: Save results
    save_results_as_txt(results)
    save_results_as_pdf(results)

    return {
        "message": "Analysis complete",
        "files": {
            "json": str(EXTRACTED_JSON),
            "csv": str(RESULT_CSV),
            "xlsx": str(RESULT_XLSX),
            "txt": str(RESULT_TXT),
            "pdf": str(RESULT_PDF)
        }
    }


@app.get("/download/{file_type}")
async def download_file(file_type: str):
    file_map = {
        "json": EXTRACTED_JSON,
        "csv": RESULT_CSV,
        "xlsx": RESULT_XLSX,
        "txt": RESULT_TXT,
        "pdf": RESULT_PDF
    }
    if file_type not in file_map:
        return JSONResponse({"error": "Invalid file type"}, status_code=400)
    return FileResponse(file_map[file_type], filename=file_map[file_type].name)