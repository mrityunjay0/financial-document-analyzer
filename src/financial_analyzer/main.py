import os
os.environ["OPENAI_API_KEY"] = "YOUR API KEY"
import pandas as pd, json
from pathlib import Path
from src.financial_analyzer.utils.analysis import analyze_financials
from src.financial_analyzer.utils.pdf_extractor import save_extracted

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet


from reportlab.lib.pagesizes import letter

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SAMPLE_PDF = DATA_DIR / "sample.pdf"
EXTRACTED_JSON = DATA_DIR / "extracted.json"
RESULT_TXT = DATA_DIR / "analysis_result.txt"
RESULT_PDF = DATA_DIR / "analysis_result.pdf"


def save_results_as_txt(results: str):
    with open(RESULT_TXT, "w", encoding="utf-8") as f:
        f.write(results)
    print(f"Results saved to {RESULT_TXT}")


def save_results_as_pdf(results: str):
    pdf_path = RESULT_PDF
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    # Split results into lines
    lines = results.split("\n")
    table_data = []

    # Convert lines to table rows
    for line in lines:
        if line.strip() == "":
            continue
        table_data.append([Paragraph(line, styles['Normal'])])

    # Create table
    table = Table(table_data, colWidths=[500])
    table.setStyle(
        TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ])
    )

    elements.append(table)
    doc.build(elements)
    print(f"Results saved as table in {pdf_path}")


def run(pdf_path: str = None, company: str = "Unknown", quarter: str = ""):
    pdf_path = pdf_path or str(SAMPLE_PDF)
    if not Path(pdf_path).exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    # Step 1: Extract PDF → JSON
    save_extracted(pdf_path, str(EXTRACTED_JSON))
    print("Saved extracted JSON to", EXTRACTED_JSON)

    # Step 2: Save as CSV & Excel
    with open(EXTRACTED_JSON, "r") as f:
        data = json.load(f)

    df = pd.DataFrame(data)
    df.to_csv(DATA_DIR / "extracted.csv", index=False)
    df.to_excel(DATA_DIR / "extracted.xlsx", index=False)
    print("Table saved as extracted.csv and extracted.xlsx")
    print(df.head())

    # Step 3: Analyze
    results = analyze_financials(str(EXTRACTED_JSON), company=company, quarter=quarter)
    print("\n📊 AI-Powered Financial Analysis:\n")
    print(results)

    # Step 4: Save results to txt & pdf
    save_results_as_txt(results)
    save_results_as_pdf(results)

    try:
        results = analyze_financials(str(EXTRACTED_JSON), company=company, quarter=quarter)
    except Exception as e:
        print(f"Analysis failed: {e}")
        results = "Analysis could not be completed due to LLM API error."


if __name__ == "__main__":
    run(company="Tesla", quarter="Q2 2024")