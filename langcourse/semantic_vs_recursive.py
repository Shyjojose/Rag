import os
import numpy as np
from dotenv import load_dotenv

# Native SDK and stable LangChain splitting only
from google import genai
from sklearn.metrics.pairwise import cosine_similarity
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

load_dotenv()

document_text = (
    "The Model Context Protocol allows developers to build open connections between AI agents and local servers. "
    "It uses standard JSON-RPC over stdio and HTTP transports to safely pipe commands. "
    "To create a perfectly crispy Neapolitan pizza crust, you must use high-hydration type 00 flour. "
    "Bake it in an oven reaching at least 900 degrees Fahrenheit for approximately 90 seconds."
)

print("=== 1. RUNNING RECURSIVE SPLITTER ===")
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=100, 
    chunk_overlap=20, 
    separators=["\n\n", "\n", " ", ""]
)
recursive_chunks = text_splitter.split_text(document_text)
for i, chunk in enumerate(recursive_chunks):
    print(f"Chunk {i+1}: {chunk}")


print("\n=== 2. RUNNING NATIVE GEMINI SEMANTIC CHUNKER ===")

embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")


# Tokenize paragraphs dynamically into standard sentences
sentences = [s.strip() + "." for s in document_text.split(".") if s.strip()]

embedding_vectors = embeddings.embed_documents(sentences)

semantic_chunks = []
current_chunk = [sentences[0]]


for i in range(len(embedding_vectors) - 1):
    vec1 = np.array(embedding_vectors[i]).reshape(1, -1)
    vec2 = np.array(embedding_vectors[i+1]).reshape(1, -1)
    
    # Evaluate math similarity between consecutive strings
    similarity = cosine_similarity(vec1, vec2)
    
    # If content meaning drops significantly (e.g. protocol tech shifts to pizza dough)
    if similarity < 0.70: 
        semantic_chunks.append(" ".join(current_chunk))
        current_chunk = [sentences[i+1]]
    else:
        current_chunk.append(sentences[i+1])

semantic_chunks.append(" ".join(current_chunk))

# Format the clean arrays back into native LangChain Documents for your RAG pipeline
semantic_docs = [Document(page_content=chunk) for chunk in semantic_chunks]

for i, doc in enumerate(semantic_docs):
    print(f"Chunk {i+1}:\n{doc.page_content}\n")

if __name__ == "__main__":
    pass
