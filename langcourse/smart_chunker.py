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
    "If the api call is done in the same sentence as the protocol description, it should be chunked together. "
    "To create a perfectly crispy Neapolitan pizza crust, you must use high-hydration type 00 flour. "
    "Bake it in an oven reaching at least 900 degrees Fahrenheit for approximately 90 seconds."
)


print("=== semantic chunker with fallback to recursive ===")
def smart_chunker(text: str, use_semantic: bool = True, similarity_threshold: float = 0.70):
    if use_semantic:
        try:

            embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
            sentences = [s.strip() + "." for s in text.split(".") if s.strip()]
            embedding_vectors = embeddings.embed_documents(sentences)

            semantic_chunks = []
            current_chunk = [sentences[0]]
            for i in range(len(embedding_vectors) - 1):
                vec1 = np.array(embedding_vectors[i]).reshape(1, -1)
                vec2 = np.array(embedding_vectors[i+1]).reshape(1, -1)
                
                similarity = cosine_similarity(vec1, vec2)
                
                if similarity < similarity_threshold: 
                    semantic_chunks.append(" ".join(current_chunk))
                    current_chunk = [sentences[i+1]]
                else:
                    current_chunk.append(sentences[i+1])
            semantic_chunks.append(" ".join(current_chunk))
            return semantic_chunks , 'semantic'
        except Exception as e:
            print(f"Semantic chunking failed with error: {e}. Falling back to recursive splitting.")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=100, 
        chunk_overlap=20, 
        separators=["\n\n", "\n", " ", ""]
    )
    return text_splitter.split_text(text)           
chunks = smart_chunker(document_text, use_semantic=True, similarity_threshold=0.60)
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}: {chunk}")      

if __name__ == "__main__":
    pass