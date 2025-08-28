import os
import json
from typing import List
import openai

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENAI_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_KEY:
    raise RuntimeError("OPENAI_API_KEY not set. Put it in environment or .env and restart.")
openai.api_key = OPENAI_KEY

# Adjustable params
DEFAULT_MODEL = os.getenv("ANALYSIS_MODEL", "gpt-4o-mini")  # cheaper alternative; change to your org's allowed model
MAX_CHUNKS = 6


def _score_and_select_chunks(chunks: List[dict], top_k: int = MAX_CHUNKS) -> List[str]:
    """Heuristic: score chunks by presence of financial keywords and length, return top_k chunk texts."""
    keywords = [
        "revenue", "income", "net", "eps", "earnings", "profit", "loss", "assets", "liabilities",
        "cash", "debt", "margin", "ebitda", "operat", "gross", "cost", "capex", "guidance", "forecast"
    ]
    scored = []
    for c in chunks:
        text = c.get("chunk", "")
        low = text.lower()
        score = sum(low.count(k) for k in keywords)
        score += min(5, len(text) // 1000)  # small boost for longer chunks
        scored.append((score, text[:4000]))  # clip each chunk to 4k chars for safety
    # sort by score, take top_k
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [t for s, t in scored[:top_k] if t.strip()]
    # if nothing selected (rare), fall back to first N chunks
    if not selected and chunks:
        selected = [c.get("chunk","")[:4000] for c in chunks[:top_k]]
    return selected


def _build_prompt(company: str, quarter: str, selected_texts: List[str]) -> (str, str):
    """Return (system_prompt, user_prompt) pair."""
    system = (
        "You are a senior equity analyst, crisp and professional. "
        "You will produce machine-readable JSON and then a short human summary. "
        "The JSON must follow this schema exactly:\n"
        "{\n"
        "  \"investment_recommendations\": [{\"action\":\"Buy|Hold|Sell\",\"rationale\":\"...\",\"confidence\":0-100}],\n"
        "  \"risk_assessment\": [{\"risk\":\"short label\",\"severity\":\"Low|Medium|High\",\"explanation\":\"...\"}],\n"
        "  \"market_insights\": [\"insight 1\", \"insight 2\", \"insight 3\"]\n"
        "}\n\n"
        "Output JSON only first (no extra text). After the JSON, print a short human-readable executive summary (3-8 bullet points). Keep the tone professional and concise."
    )

    # Compose a compact context to keep tokens reasonable
    context = "\n\n---\n\n".join(selected_texts)
    user = f"Company: {company or 'Unknown'}\nQuarter: {quarter or 'Unknown'}\n\nContext (extracted text fragments):\n{context}\n\nInstructions: Produce the JSON described above and then a short executive summary. Be concise, emphasize investment action, key risks, and market drivers."
    return system, user


def analyze_financials(json_path: str, company: str = None, quarter: str = None, model: str = DEFAULT_MODEL) -> str:
    """
    Main entrypoint.
    - json_path: path to extracted.json
    - returns: string (pretty-printed JSON + plain text)
    """
    # 1) Load extracted chunks
    with open(json_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)

    # 2) Select most relevant chunks
    selected = _score_and_select_chunks(chunks, top_k=MAX_CHUNKS)

    # 3) Build prompt pair
    system_prompt, user_prompt = _build_prompt(company or "Unknown", quarter or "Unknown", selected)

    # 4) Call OpenAI chat completions
    try:
        resp = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.0,
            max_tokens=1000,
        )
        content = resp.choices[0].message.content.strip()
    except Exception as e:
        # bubble up a clear error string
        raise RuntimeError(f"LLM call failed: {e}")

    # 5) Try to separate JSON block and human summary
    # Expectation: JSON object first, then plain text.
    json_part = None
    text_part = None
    # attempt to find first opening brace and last closing brace to extract JSON (best-effort)
    try:
        start = content.index("{")
        end = content.rindex("}") + 1
        json_raw = content[start:end]
        parsed = json.loads(json_raw)
        json_part = parsed
        text_part = content[end:].strip()
    except Exception:
        # fallback: try to parse whole content as JSON
        try:
            parsed = json.loads(content)
            json_part = parsed
            text_part = ""
        except Exception:
            # give up parsing — return raw content, but in a predictable wrapper
            return f"UNPARSED_RESPONSE:\n{content}"

    # 6) Create a pretty output string: JSON pretty + human summary
    pretty_json = json.dumps(json_part, indent=2, ensure_ascii=False)
    human_summary = text_part or ""
    output = f"{pretty_json}\n\n---\n\nExecutive Summary:\n{human_summary}"
    return output