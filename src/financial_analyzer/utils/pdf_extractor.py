import fitz  # PyMuPDF
import json
from pathlib import Path
from typing import List

CHUNK_SIZE = 2000  # characters per chunk - tune as needed

def extract_text_chunks(pdf_path: str) -> List[dict]:
    doc = fitz.open(pdf_path)
    chunks = []
    current = ""
    chunk_id = 0
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        text = text.strip()
        if not text:
            continue
        # simple whitespace normalization
        text = "\n".join([line.strip() for line in text.splitlines() if line.strip()])
        # append and chunk
        current += "\n\n" + text
        while len(current) >= CHUNK_SIZE:
            chunk_text = current[:CHUNK_SIZE]
            chunks.append({"id": chunk_id, "page": page_num + 1, "chunk": chunk_text})
            chunk_id += 1
            current = current[CHUNK_SIZE:]
    if current.strip():
        chunks.append({"id": chunk_id, "page": page_num + 1, "chunk": current})
    return chunks

def save_extracted(pdf_path: str, output_path: str):
    chunks = extract_text_chunks(pdf_path)
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)
    return output_path

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python pdf_extractor.py <input.pdf> <output.json>")
        sys.exit(1)
    print(save_extracted(sys.argv[1], sys.argv[2]))
