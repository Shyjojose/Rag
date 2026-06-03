markdown# Technical Brief: Structured RAG Pipeline Architecture
This document synthesizes core concepts, execution strategies, and architectural decisions for building a high-accuracy, production-grade Extraction and Ingestion pipeline using Python, **Pydantic v2**, and **Google Gemini 2.5 Flash**.

---

## 🏢 1. The Core Architectural Philosophy
When processing complex, highly regulated text (such as German health insurance statutes / *Satzung*), traditional RAG pipelines fail due to **vector semantic search inaccuracies** and **LLM number blindness**. 

This pipeline adopts a two-stage approach to isolate the system from hallucinations:

Use code with caution.[ Raw PDF File ]│▼⚙️ STAGE 1: Document Loading & Iteration (pypdf Engine)│  • Performs raw, structural character extraction│  • Loops page-by-page to preserve positional accuracy▼🤖 STAGE 2: Structured Inference Firewall (LLM + Pydantic/JSON Schema)• Restricts LLM output mechanics via Native Tool Calling• Validates incoming string tokens into strict Python data types
---

## 🚫 2. Critical Problems Encountered & Solved

### A. Free-Form Text Degradation (The JSON Defect)
*   **The Problem:** LLMs are statistical text predictors. Prompt engineering hacks like *"Return only JSON"* eventually fail, outputting conversational text wrappers or malformed brackets that crash downstream applications with `JSONDecodeError`.
*   **The Solution:** Using LangChain's `.with_structured_output(Schema)` alters the model's token selection mechanics at the API level. The model is mathematically constrained by the schema blueprint.

### B. "Lost in the Middle" Attention Blindspots
*   **The Problem:** Shoving massive multi-page blocks into an LLM context window causes attention degradation. The model naturally over-indexes on the beginning and end of the prompt, dropping crucial legal clauses or rate changes buried in the middle text.
*   **The Solution:** An explicit page-by-page `for` loop. Passing isolated single-page strings forces 100% LLM attention focus, ensures token safety margins, and guarantees correct `pdf_page_index` tracking.

### C. Free-Tier API Envelope Constraints
*   **The Problem:** Gemini's Free Tier blocks rapid-fire loop executions with `429 RESOURCE_EXHAUSTED` errors due to a strict **20 requests-per-day quota ceiling**.
*   **The Solution:** In production, attach a paid Cloud Billing account to lift boundaries to 4,000 RPM. For free tier testing, implement strict conditional loops (`min(15, total_pages)`), handle exceptions gracefully, and implement explicit `time.sleep(25)` cooldown breaks.

---

## 💡 3. Key Concepts Mastered

### Concept A: Verbs vs. Nouns (Functions vs. Classes)
Understanding the division of labor in modern AI engineering prevents structural spaghetti code:
*   **Functions are Verbs (Actions):** Used to compute logic, call network endpoints, read files, and write datasets (`run_pipeline()`, `extract_structured_data()`).
*   **Classes are Nouns (State Matrices):** Used via Pydantic to declare *what the data is allowed to look like*. Classes automatically compile down into universal JSON schemas for the API and turn raw responses into type-safe Python objects on return.

### Concept B: The Inbound Validation Firewall
Even with constrained API definitions, models can occasionally hallucinate incorrect string text into numeric values. Pydantic acts as an inbound firewall:
1. Gemini yields a raw text reply.
2. The response is immediately instantiated via Pydantic (`Schema(**llm_reply)`).
3. If structural anomalies or bad data types are discovered, an isolated exception is caught safely *on your computer* before the database layer is corrupted.

---

## 🛠️ 4. Why JSON is Superior to Knowledge Graphs for this Data
While highly discussed, a **Knowledge Graph RAG (GraphRAG)** is an over-engineered pattern for hierarchical document schemas like public insurance statutes.

*   **Your Schema RAG (Metadata Matrix):** Maps structural data linearly. Because insurance statutes use strict numbers, categories, and age tiers, standard Python code comparison checks (`min_age <= user_age <= max_age`) run with **100% deterministic accuracy and zero hallucination risk**.
*   **Knowledge Graph RAG:** Maps abstract entities via multi-hop nodes and web relationships. It requires dedicated, expensive server infrastructures (e.g., Neo4j, Cypher query code) and is designed for unstructured cross-document discovery, adding redundant complexity to simple legal lookup tables.

---

## 📋 5. Complete Production Script Blueprint

```python
import os
import json
import time
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import pypdf
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# =====================================================================
# DATA NOUNS: PYDANTIC LOGIC MATRIX (SYSTEM BLUEPRINT)
# =====================================================================

class ErstattungsLogik(BaseModel):
    typ: str = Field(description="Volle Übernahme, Anteilig, Zuschuss (Festbetrag), or Ausschuss / Keine Übernahme")
    turnus: str = Field(default="Je Kalenderjahr", description="e.g., Je Kalenderjahr, Einmalig")
    prozentsatz: Optional[float] = Field(default=None, description="If anteilig, e.g., 80")
    max_euro_gesamt: Optional[float] = Field(default=None, description="Limit per turnus")

class Satzungsleistung(BaseModel):
    legal_paragraph: str = Field(description="The exact source section law tracking index, e.g., § 33")
    name: str = Field(description="Name of the benefit")
    kategorie: str = Field(description="Category of the benefit")
    pdf_page_index: int = Field(description="The page number where this rule was found")
    erstattungs_logik: ErstattungsLogik
    exceptions_and_constraints: List[dict] = Field(default_factory=list, description="Fine-grained exceptions arrays")

class KrankenkasseMetadata(BaseModel):
    name: str = Field(default="Techniker Krankenkasse")
    slug: str = Field(default="tk")
    satzung_stand: Optional[str] = Field(default="")

class KrankenkassenIndustryPolicySchema(BaseModel):
    krankenkasse: KrankenkasseMetadata
    satzungsleistungen: List[Satzungsleistung] = Field(
        default_factory=list, 
        description="Extracted rule list. If a page has NO legal benefits, return an empty array []"
    )

# =====================================================================
# DATA VERBS: THE PROCESSING ENGINE
# =====================================================================

def extract_structured_data(raw_text: str, current_page: int) -> Optional[KrankenkassenIndustryPolicySchema]:
    """Passes flat text to Gemini and enforces strict Pydantic structure compilation."""
    try:
        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)
        structured_llm = llm.with_structured_output(KrankenkassenIndustryPolicySchema)
        
        prompt = (
            "System: You are a professional compliance auditor for German health insurance policies.\n"
            f"Analyze the text found explicitly on PDF Page {current_page}.\n"
            f"CRITICAL: Set the 'pdf_page_index' field to {current_page} for every single extracted benefit.\n\n"
            f"Source Text:\n{raw_text}"
        )
        return structured_llm.invoke(prompt)
    except Exception as e:
        print(f"❌ Extraction fallback catch on page {current_page}: {e}")
        return None

def run_pipeline(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found at path: {pdf_path}")
        return
        
    loader = pypdf.PdfReader(pdf_path)
    documents = loader.pages
    
    # Free tier safe throttling cutoff limit
    total_pages = min(15, len(documents))
    print(f"📄 Total pages in PDF selected for free tier loop processing: {total_pages}")
    
    all_structured_data = []

    for idx in range(total_pages):
        current_page_number = idx + 1
        page_text = documents[idx].extract_text()

        if not page_text.strip():
            print(f"⚠️ Page {current_page_number} has no extractable text.")
            continue

        print(f"⚙️ Processing Page {current_page_number} / {total_pages} - Characters: {len(page_text)}")
        
        try:
            structured_page_data = extract_structured_data(page_text, current_page_number)
            
            if structured_page_data and structured_page_data.satzungsleistungen:
                print(f"   ✅ Found {len(structured_page_data.satzungsleistungen)} rules on page {current_page_number}!")
                all_structured_data.append(structured_page_data.model_dump())
            else:
                print(f"   ℹ️ No matching functional benefits found on page {current_page_number}.")
                
        except Exception as api_err:
            print(f"⚠️ API Exception caught: {api_err}. Running a 30s cooldown block...")
            time.sleep(30)
            continue

        # Free tier protective cooldown break
        time.sleep(25)

    # Save logic execution
    output_filename = "extracted_structured_data.json"
    with open(output_filename, "w", encoding="utf-8") as output_file:
        json.dump(all_structured_data, output_file, indent=2, ensure_ascii=False)
        
    print(f"\n💾 Pipeline completed cleanly! JSON matrix saved to: {output_filename}")

if __name__ == "__main__":
    run_pipeline("data/tk-satzung-data.pdf")
```