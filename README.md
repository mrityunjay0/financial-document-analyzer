# 📊 Financial Document Analyzer (FDA)

A FastAPI-based application that extracts data from financial reports (PDFs), analyzes key insights using LLMs, and generates outputs in multiple formats (JSON, CSV, Excel, PDF).

---

## Features

- Upload any financial PDF report.
- Extracts text and tabular data into structured JSON.
- Performs AI-powered financial analysis.
- Exports results to:
  - JSON (`extracted.json`)
  - CSV (`extracted.csv`)
  - Excel (`extracted.xlsx`)
  - PDF (`analysis_result.pdf`, formatted as table)
- REST API built with **FastAPI**.

---

## Tech Stack

- **Python 3.12+**
- **FastAPI** → REST API for PDF uploads & results.
- **Pydantic** → Data validation.
- **OpenAI API** → LLM-powered financial insights.
- **ReportLab** → Generate PDF reports.
- **Pandas** → CSV & Excel exports.
- **PyPDF2 / pdfplumber** → PDF text extraction.
- **Uvicorn** → ASGI server.

---

## Project Structure

src/
│── data/                # Sample PDFs & extracted files
│── financial_analyzer/
│   │── config/          # .env, agents.yaml, tasks.yaml
│   │── utils/           # core utilities
│   │   ├── analysis.py
│   │   ├── pdf_extractor.py
│   │   ├── crew.py
│   │   ├── main.py
│   │── app.py           # FastAPI app entrypoint
tests/                   # Unit tests
README.md                # Project documentation
requirements.txt         # Dependencies

---

##  Setup & Installation

1. **Clone the repo**
```Bash
   git clone https://github.com/mrityunjay0/financial-document-analyzer.git
   cd financial-document-analyzer
   ```
2.	**Create a virtual environment**
```Bash
    python3 -m venv .venv
    source .venv/bin/activate   # macOS/Linux
    .venv\Scripts\activate      # Windows
```
3. **Install dependencies**
```Bash
    pip install -r requirements.txt
```
4. **Configure environment**
```Bash
    OPENAI_API_KEY=sk-xxxxxx
```
## Run the Project

1. Run CLI Mode:
```Bash
    python src/financial_analyzer/main.py
```
2. Run FastAPI Server:
```Bash
    cd src
    uvicorn financial_analyzer.app:app --reload
```
## Outputs:

	•	extracted.json → Raw extracted chunks
	•	extracted.csv / extracted.xlsx → Structured tabular data
	•	analysis_result.pdf → Final insights in table format

## Bugs & Fixes:

1. FastAPI Import Error (Error loading ASGI app)

	•	Cause: Ran uvicorn app:app --reload while app.py was inside src/financial_analyzer/. Python couldn’t find the module.

	•	Fix: Corrected the module path to:
        uvicorn src.app:app --reload

2. No Output File Generated (analysis results missing)

	•	Cause: analysis.py returned a string but no logic existed to write output into a file.

	•	Fix: Added file writers (with open(...)) for .txt, .pdf, .csv, and .xlsx.

	•	Used Pandas for CSV/Excel.

	•	Used ReportLab for PDF with tables.

3. PDF Output Not in Table Format

	•	Cause: Initial PDF export was plain text (not structured).

	•	Fix: Used reportlab.platypus.Table to format financial analysis into a table inside analysis_result.pdf.

4. Confusion Between CLI Mode & API Mode

	•	Cause: Both main.py and app.py existed, but user tried running API via main.py.

	•	Fix: Separated execution clearly:

	•	main.py → CLI mode.

	•	app.py → FastAPI server mode.

5. Environment Variables Not Detected

	•	Cause: .env file wasn’t being loaded automatically.

	•	Fix: Installed and used python-dotenv,
        added:
        from dotenv import load_dotenv
        load_dotenv()

6. Uvicorn Hot Reload Crashes

	•	Cause: Ran uvicorn from project root instead of src/.

	•	Fix: Changed working directory to src before starting server:
```Bash
        cd src
        uvicorn src.app:app --reload
```

## Project Workflow: Financial Document Analyzer

1. Input Handling (User Upload)

	•	Interface: User uploads a financial PDF (e.g., balance sheet, annual report) through the FastAPI endpoint.

	•	The uploaded file is stored temporarily in the /data directory.

2. PDF Extraction Layer

	•	pdf_extractor.py extracts raw text and tabular data.

	•	Uses libraries like PyPDF2, pdfplumber, or camelot/tabula.

	•	Raw content is then structured into:

	•	JSON → captures structured entities.

	•	CSV → for tabular data (transactions, balances).

	•	XLSX → for Excel users & BI tools.

3. Data Preprocessing

	•	Cleaned data (JSON/CSV/XLSX) is stored in /data.

4. AI-Powered Financial Analysis

	•	Once structured data is ready, OpenAI API is called.

	•	Prompt includes the JSON/CSV content → model returns:

	•	Investment Recommendations

	•	Risk Analysis

	•	Market Trends / Insights

5. Report Generation

	•	Results from OpenAI are converted into:

	•	PDF Summary Report (using reportlab)

6. Error Handling / Bugs Fixed

	•	ASGI Import Error (Could not import app) → fixed by pointing to correct module:
```Bash
uvicorn src.financial_analyzer.app:app --reload
```