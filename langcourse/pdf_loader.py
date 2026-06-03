import os
import pypdf
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_google_genai import ChatGoogleGenerativeAI
load_dotenv()
from typing import List, Optional
from pydantic import BaseModel, Field


pdf_path = "data/tk-satzung-data.pdf"

class ErstattungsLogik(BaseModel):
    typ: str = Field(...)
    turnus: str = Field(default="Je Kalenderjahr")
    prozentsatz: Optional[float] = None
    max_euro_einzeln: Optional[float] = None
    max_euro_gesamt: Optional[float] = None


class Satzungsleistung(BaseModel):
    legal_paragraph: str
    name: str
    kategorie: str
    beschreibung_kurz: Optional[str] = None
    pdf_page_index: int
    erstattungs_logik: ErstattungsLogik
    exceptions_and_constraints: List[dict] = Field(default_factory=list)
    eligibility_rules: List[dict] = Field(default_factory=list)


class KrankenkasseMetadata(BaseModel):
    name: str = Field(default="Techniker Krankenkasse")
    slug: str = Field(default="tk")
    satzung_stand: Optional[str] = None


class KrankenkassenIndustryPolicySchema(BaseModel):
    krankenkasse: KrankenkasseMetadata
    satzungsleistungen: List[Satzungsleistung] = Field(default_factory=list)


def doc_structure() -> dict:
    DOCUMENT = {
        "$schema": "http://json-schema.org",
        "title": "KrankenkassenIndustryPolicySchema",
        "type": "object",
        "properties": {
            "krankenkasse": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "slug": {"type": "string"},
                    "satzung_stand": {"type": "string"},
                    "global_budgets": {
                        "type": "array",
                        "description": "Shared monetary caps across multiple different benefit categories (e.g., Gesundheitskonto).",
                        "items": {
                            "type": "object",
                            "properties": {
                                "budget_id": {"type": "string", "description": "e.g., gesunder_lebensstil_konto"},
                                "max_amount": {"type": "number"},
                                "currency": {"type": "string"},
                                "per_turnus": {"type": "string", "description": "e.g., Kalenderjahr"}
                            },
                            "required": ["budget_id", "max_amount", "currency", "per_turnus"]
                        }
                    }
                },
                "required": ["name", "slug", "satzung_stand"]
            },
            "satzungsleistungen": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "legal_paragraph": {"type": "string", "description": "The exact source section law tracking index, e.g., § 14 Abs. 2 Satz 1"},
                        "name": {"type": "string"},
                        "kategorie": {"type": "string"},
                        "beschreibung_kurz": {"type": "string"},
                        "pdf_page_index": {"type": "integer"},
                        "erstattungs_logik": {
                            "type": "object",
                            "properties": {
                                "typ": {"type": "string", "enum": ["Volle Übernahme", "Anteilig", "Zuschuss (Festbetrag)", "Ausschuss / Keine Übernahme"]},
                                "prozentsatz": {"type": "number", "description": "If anteilig, e.g., 80"},
                                "max_euro_einzeln": {"type": "number", "description": "Limit per execution"},
                                "max_euro_gesamt": {"type": "number", "description": "Limit per turnus inside this line item alone"},
                                "turnus": {"type": "string", "description": "e.g., Je Kalenderjahr, Einmalig im Leben, Jedes 2. Jahr"},
                                "belongs_to_global_budget_id": {"type": "string", "description": "References a budget defined in global_budgets if it shares a cap"}
                            },
                            "required": ["typ", "turnus"]
                        },
                        "exceptions_and_constraints": {
                            "type": "array",
                            "description": "Fine-grained industry exceptions preventing payout.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "constraint_type": {"type": "string", "enum": ["Ausschlusskriterium", "Zusatzqualifikation", "Voraussetzung"]},
                                    "rule_text": {"type": "string", "description": "The exact clause text, e.g., 'Nur durch teilnehmende Kassenzahnärzte (BEMA)'"},
                                    "cross_reference_paragraph": {"type": "string", "description": "Points to another paragraph altering this rule if applicable"}
                                },
                                "required": ["constraint_type", "rule_text"]
                            }
                        },
                        "eligibility_rules": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "alter_min": {"type": "integer"},
                                    "alter_max": {"type": "integer"},
                                    "geschlecht": {"type": "string", "enum": ["ALL", "W", "M", "D"]},
                                    "requires_pregnancy": {"type": "boolean"},
                                    "requires_children": {"type": "boolean"}
                                },
                                "required": ["alter_min", "alter_max", "geschlecht", "requires_pregnancy", "requires_children"]
                            }
                        }
                    },
                    "required": ["legal_paragraph", "name", "kategorie", "pdf_page_index", "erstattungs_logik", "exceptions_and_constraints", "eligibility_rules"]
                }
            }
        },
        "required": ["krankenkasse", "satzungsleistungen"]
    }
    return DOCUMENT

def extract_structured_data(raw_text: str, schema: dict) -> dict:
    """Sends the raw text and schema to gemini to guarantee matching JSON output."""
    print("🤖 Processing text through LLM...")
    
    response = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature =0)

    structured_llm = response.with_structured_output(schema)

    prompt = (
        "System: You are a professional legal auditor for German health insurance policies. "
        "Analyze the text and populate the required data schema exactly.\n\n"
        f"User: Analyze this insurance policy text and map it to the structure:\n\n{raw_text}"
    )
    
    # LangChain automatically handles the parsing back into a python dict object
    return structured_llm.invoke(prompt)


def run_pipeline(pdf_path: str):
    # 1. Early return if file doesn't exist
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found at path: {pdf_path}")
        return
        
    loader = pypdf.PdfReader(pdf_path)
    documents = loader.pages
    total_pages = min(20, len(documents)) # FIX: Prevent index crash if PDF has under 20 pages
    print(f"📄 Total pages in PDF to process: {total_pages}")
    
    all_extracted_text = []
    all_structured_data = [] 
    structured_data = None    

    target_schema = doc_structure() 

    for idx in range(total_pages):
        current_page_number = idx + 1
        page_text = documents[idx].extract_text() 

        # Check for blank layout pages
        if not page_text.strip():
            print(f"⚠️ Page {current_page_number} has no extractable text.")
            continue

        print(f"✅ Extracted text from page {current_page_number} / {total_pages} - Characters: {len(page_text)}")
        all_extracted_text.append(page_text)
        
        # Call the LLM extraction step
        structured_data = extract_structured_data(page_text, target_schema)

        # Handle validation boundaries safely
        # Works perfectly whether structured_data is a dictionary or a Pydantic object
        has_benefits = False
        if structured_data:
            if hasattr(structured_data, "satzungsleistungen") and structured_data.satzungsleistungen:
                has_benefits = True
            elif isinstance(structured_data, dict) and structured_data.get("satzungsleistungen"):
                has_benefits = True

        if has_benefits:
            print(f"✅ Successfully extracted structured data from page {current_page_number}")
            
            # FIX: Convert Pydantic models to pure Python dictionaries before appending
            if hasattr(structured_data, "model_dump"):
                all_structured_data.append(structured_data.model_dump())
            elif hasattr(structured_data, "dict"):
                all_structured_data.append(structured_data.dict())
            else:
                all_structured_data.append(structured_data)

    print("\n✅ Successfully Extracted JSON Schema Data from final processed loop:")
    if structured_data:
        if hasattr(structured_data, "model_dump"):
            print(json.dumps(structured_data.model_dump(), indent=2, ensure_ascii=False))
        elif hasattr(structured_data, "dict"):
            print(json.dumps(structured_data.dict(), indent=2, ensure_ascii=False))
        else:
            print(json.dumps(structured_data, indent=2, ensure_ascii=False))

    # FIX: Clean path building logic to prevent empty string folder crashes
    output_filename = "extracted_structured_data.json"
    folder_path = os.path.dirname(output_filename)
    if folder_path: # Only create directory if a folder structure is actually specified
        os.makedirs(folder_path, exist_ok=True)
        
    with open(output_filename, "w", encoding="utf-8") as output_file:
        json.dump(all_structured_data, output_file, indent=2, ensure_ascii=False)
        
    print(f"\n✅ All structured data has been saved to: {output_filename}")

    # 1. Early return if file doesn't exist
    if not os.path.exists(pdf_path):
        print(f"❌ PDF file not found at path: {pdf_path}")
        return
        
    loader = pypdf.PdfReader(pdf_path)
    documents = loader.pages
    total_pages = 20
    print(f"📄 Total pages in PDF: {total_pages}")
    
    all_extracted_text = []
    all_structured_data = [] # FIX: Initialized the collection list
    structured_data = None    # FIX: Initialize variable for final print tracking

    # Fetch the target schema blueprint once before starting the loop
    target_schema = doc_structure() # FIX: Added target_schema initialization

    for idx in range(total_pages):
        current_page_number = idx + 1
        page_text = documents[idx].extract_text() # FIX: Uniform naming to page_text

        # Check for blank layout pages
        if not page_text.strip():
            print(f"⚠️ Page {current_page_number} has no extractable text.")
            continue

        # FIX: Repaired syntax error with proper f-string embedding
        print(f"✅ Extracted text from page {current_page_number} / {total_pages} - Characters: {len(page_text)}")
        all_extracted_text.append(page_text)
        
        # FIX: Pass the single page_text string context instead of undefined combined_text
        structured_data = extract_structured_data(page_text, target_schema)

        # Handle validation boundaries
        # Note: If extract_structured_data returns a Pydantic model object, use structured_data.satzungsleistungen
        # If it returns a dict, use structured_data.get("satzungsleistungen")
        if structured_data and getattr(structured_data, "satzungsleistungen", None):
            print(f"✅ Successfully extracted structured data from page {current_page_number}")
            all_structured_data.append(structured_data)

    print("\n✅ Successfully Extracted JSON Schema Data from document loops:")
    if structured_data:
        # If model is Pydantic, convert via .model_dump(), otherwise print directly
        if isinstance(structured_data, BaseModel):
            print(json.dumps(structured_data.model_dump(), indent=2, ensure_ascii=False))
        else:
            output_data = structured_data.get("satzungsleistungen", []) 
    output_filename ="extracted_structured_data.json"
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "w", encoding="utf-8") as output_file:
        json.dump(all_structured_data, output_file, indent=2, ensure_ascii=False)
    print(f"\n✅ All structured data has been saved to {output_filename}")


if __name__ == "__main__":
    run_pipeline(pdf_path)