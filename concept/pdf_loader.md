# Modern RAG Ingestion Pipeline — Structured Extraction

This document describes a robust, production-ready two-stage pipeline for extracting structured data from complex legal PDFs (for example, German health insurance statutes). The design focuses on separation of concerns, strict validation, and safe LLM integration.

## Architecture Overview

- Raw PDF File
  - Stage 1: Document Loading (dumb extraction)
    - Uses a PDF loader (e.g., `PyPDFLoader` or `pypdf`) to extract page-by-page text
    - Produces raw `page_content` strings
  - Stage 2: Structured Inference & Validation
    - Sends single-page text to an LLM with an attached JSON Schema / Pydantic model
    - Uses Pydantic v2 for type validation and safe model conversion

Advantages of this separation:

- Keeps LLM context small (page-by-page)
- Makes invalid outputs catchable via typed validation
- Enables deterministic downstream processing and indexing

## Data Models (conceptual)

Use Pydantic models to declare the canonical schema you expect from the LLM. Example concepts:

- `ErstattungsLogik` — reimbursement logic (type, turnus, percent, caps)
- `Satzungsleistung` — a single benefit line item (legal paragraph, name, category)
- `KrankenkasseMetadata` — metadata about the insurer (name, slug, statute date)
- `KrankenkassenIndustryPolicySchema` — top-level container with metadata and a list of benefits

These models serve two purposes:

1. They compile into a JSON Schema that can be attached to LLM calls (structured output).
2. They validate and cast LLM return payloads into typed Python objects.

## Processing Workflow

1. Load the PDF and iterate pages individually.
2. For each page: skip if blank; otherwise call the LLM with the page text and the compiled schema.
3. Validate the LLM response using Pydantic. If validation fails, log the error and continue.
4. On success, persist the typed object (serialize to JSON, save to DB, or index into vector store).

Example (pseudo) flow:

```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("data/tk-satzung-data.pdf")
pages = loader.load()
for page in pages:
    if not page.page_content.strip():
        continue
    structured = call_llm_with_schema(page.page_content)
    if structured:
        save(structured.model_dump())
```

## Common Failure Modes & Mitigations

- Dumb extraction loses layout and tables — mitigate by pre-processing (OCR, layout heuristics) when needed.
- LLM free-form outputs cause JSON parse errors — mitigate by using structured output (LangChain / provider structured APIs) + Pydantic validation.
- Context loss over long documents — mitigate by page-by-page processing and explicit cross-reference linking when aggregating results.
- Transient network or API errors — catch exceptions, backoff and retry, log failures and continue processing other pages.

## Production Rules / Best Practices

- Process sequentially (page-by-page) to preserve `pdf_page_index` accuracy.
- Design schemas to be permissive where appropriate (use `Optional` and `default_factory=list`).
- Enforce strict enums and numeric types for critical fields (percentages, money caps).
- Log and surface validation failures for manual review; do not crash the entire job.

## Next Steps and Integrations

- Add a minimal unit test to validate that an example page maps to the expected schema.
- Add persistence: store validated entries as JSON in a DB or index into a vector store for RAG.
- Add retry/backoff wrappers around the LLM call for robustness.

If you want, I can:

- produce a small runnable example with `pyproject.toml` and tests,
- or convert the conceptual models shown here into a ready-to-run `pdf_loader.py` implementation.
