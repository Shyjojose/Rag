from dotenv import load_dotenv
import tempfile
import os
from langchain_community.document_loaders import TextLoader
from langchain_google_genai import ChatGoogleGenerativeAI
# Load your environment variables (Ensure GOOGLE_API_KEY is inside your .env file)
load_dotenv()

def load_document():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(b"Hello, this is a test document.")
        temp_path = temp_file.name


    try:
        lader = TextLoader(temp_path)
        documents = lader.load()

        print("Loaded document content:", len(documents))
        print(f"Document content type: {type(documents)}")
        print(f"metadata: {documents[0].metadata}")

        for doc in documents:
            print(doc.page_content)
    finally:
        os.remove(temp_path)

if __name__ == "__main__":
    load_document()
    
