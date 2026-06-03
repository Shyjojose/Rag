langchain has objects to load documants 

raw files .pdf .txt .html 
document loader makes 
-lis[document]
- pagecontent

PyPDFLoader pdf 
TextLoader plain text
DirectoryLoader Multiple files folder/*
WebBaseLoader Web pages https://
UnstructuredLoader  complex docs mixed

# PDF Loaders
pdf metadata -> its a dictionary containig foundational feild 
{
    soruce: ,
    page : ,
    title: ,
    author: ,
    keyowrd: , 
}

-- Empty Fields: If the human who created the PDF didn't fill out the Title or Author fields in Word/Acrobat before exporting, those keys will either be missing or return an empty string "". Only source and page are guaranteed.
--Date Format: Notice the strange date string (D:20260315...). This is the standard PDF epoch format. It reads as: Year (2026), Month (03), Day (15), Hour (14), Minute (32), Second (05).

# pdf module
PyPDFLoader - good for simple pdf, basic meta data, simple pdf 
PyMuPDFLoader           - fastest , rich metadata , high volume pdf
UnstructuredPDFLoader   - slower, detailed metadata, tables and loayouts
'''
from langchain_community.document_loaders import PyPDFLoade
loader = PyPDFLoader("sample_report.pdf")
pages = loader.load()
first_page = pages[0]
print("--- Content Snippet ---")
print(first_page.page_content[:150]) # First 150 characters of text
print("\n--- Extracted Metadata Object ---")
print(first_page.metadata)

# web loading 
url -> web based loader -> document 
multiple url -> web based loader -> document0, document1, document2

# directory loading 
docs/ 
report.pdf
notesx.txt
data.csv 
guide.pdf 
glob pattern filters files "**/.pdf" = all pdf in all subdirectories 

import os
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader

def load_all_documents():
    path = "./documents"
    
    if not os.path.exists(path):
        print(f"❌ Error: The directory '{path}' does not exist.")
        return

    print(f"📂 Scanning directory: {path}...")

    # Initialize DirectoryLoader
    # glob="**/*.pdf" ensures it looks for PDFs in the main folder and subfolders
    loader = DirectoryLoader(
        path,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader,  -----> this Tells which pdf loader to use
        show_progress=True         ----> show visual progress bar
    )

    # Load all documents into memory
    docs = loader.load()
    
    print(f"\n✅ Successfully loaded {len(docs)} total pages from the directory.")
    
    # Show an example of the metadata structured from the batch load
    if docs:
        print("\n--- Example Metadata from Batch Load ---")
        print(f"Source File: {docs[0].metadata['source']}")
        print(f"Page Number: {docs[0].metadata['page']}")

if __name__ == "__main__":
    load_all_documents()


