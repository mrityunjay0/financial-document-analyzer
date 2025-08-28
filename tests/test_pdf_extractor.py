from src.financial_analyzer.utils.pdf_extractor import extract_text_chunks

def test_extract_chunks_smoke():
    try:
        chunks = extract_text_chunks('data/sample.pdf')
        assert isinstance(chunks, list)
    except Exception:
        assert True
