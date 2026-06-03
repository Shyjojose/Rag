# Production RAG

This repository contains a small set of LangChain and Gemini experiments for building a retrieval-augmented generation workflow. The code focuses on four practical areas:

- loading documents from files and PDFs,
- experimenting with chunking strategies,
- trying hybrid retrieval with BM25 + vector search,
- extracting structured data from a PDF into JSON using a Pydantic schema.

The main runnable code lives in [langcourse/](langcourse/), while [concept/](concept/) contains notes and design ideas for the RAG pipeline.

## Project Structure

- [concept/](concept/) - architecture notes and implementation ideas for RAG, chunking, PDF loading, and observability.
- [data/](data/) - sample input data, including `tk-satzung-data.pdf`.
- [langcourse/](langcourse/) - Python package with the runnable examples.
- [langcourse/main.py](langcourse/main.py) - simple Gemini call that prints a response.
- [langcourse/load_document.py](langcourse/load_document.py) - document loading example.
- [langcourse/text_spliters.py](langcourse/text_spliters.py) - chunking experiments.
- [langcourse/hybrid_search.py](langcourse/hybrid_search.py) - hybrid retrieval example.
- [langcourse/pdf_loader.py](langcourse/pdf_loader.py) - structured extraction pipeline for the PDF.

## Requirements

- Python 3.11 or newer
- A Google Gemini API key in your environment as `GOOGLE_API_KEY`
- The sample PDF at [data/tk-satzung-data.pdf](data/tk-satzung-data.pdf) for the PDF extraction demo

## Setup

1. Go into the package directory:

	```bash
	cd "langcourse"
	```

2. Create or sync the virtual environment with `uv`:

	```bash
	uv sync
	```

	If you prefer `venv`, create and activate it manually, then install the dependencies from `pyproject.toml`.

3. Create a `.env` file in `langcourse/` with your API key:

	```env
	GOOGLE_API_KEY=your_api_key_here
	```

## Run the examples

Run any of the scripts directly from the `langcourse/` folder:

```bash
python main.py
python load_document.py
python text_spliters.py
python hybrid_search.py
python pdf_loader.py
```

## What the scripts do

`main.py` sends a prompt to Gemini and prints the response. `text_spliters.py` compares different chunking approaches. `hybrid_search.py` demonstrates a hybrid retriever pattern using vector search plus BM25. `pdf_loader.py` reads the sample PDF, sends each page through a structured LLM extraction step, and writes the result to `extracted_structured_data.json`.

## Notes

- The repository is intended as an experimentation workspace, so some files are intentionally lightweight or exploratory.
- The PDF extraction script expects the Gemini client to be available and will fail if `GOOGLE_API_KEY` is not set.
- Generated output such as `extracted_structured_data.json` is not committed by default.
