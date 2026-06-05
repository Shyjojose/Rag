import os
import json
import numpy as np
import warnings
from dotenv import load_dotenv

from sklearn.metrics.pairwise import cosine_similarity
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

warnings.filterwarnings("ignore", category=UserWarning)
load_dotenv()

document_text = (
    "The Model Context Protocol allows developers to build open connections between AI agents and local servers. "
    "It uses standard JSON-RPC over stdio and HTTP transports to safely pipe commands. "
    "If the api call is done in the same sentence as the protocol description, it should be chunked together. "
    "To create a perfectly crispy Neapolitan pizza crust, you must use high-hydration type 00 flour. "
    "Bake it in an oven reaching at least 900 degrees Fahrenheit for approximately 90 seconds."
)

def smart_chunker(text: str, use_semantic: bool = True, similarity_threshold: float = 0.40):
    if use_semantic:
        try:
            print(f"🧠 Initializing Local Embedding Model using threshold: {similarity_threshold}")
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            
            # Clean and isolate sentences
            sentences = [s.strip() + "." for s in text.split(".") if s.strip()]
            embedding_vectors = embeddings.embed_documents(sentences)

            semantic_chunks = []
            # ✅ FIX: Initialize as a flat list containing only the first sentence string
            current_chunk = [sentences[0]]
            
            for i in range(len(embedding_vectors) - 1):
                vec1 = np.array(embedding_vectors[i]).reshape(1, -1)
                vec2 = np.array(embedding_vectors[i+1]).reshape(1, -1)
                
                similarity = cosine_similarity(vec1, vec2)[0][0]
                print(f"   ↳ Similarity between sentence {i+1} and {i+2}: {similarity:.4f}")
                
                if similarity < similarity_threshold: 
                    # Topic shift! Save the accumulated sentences as a chunk
                    semantic_chunks.append(" ".join(current_chunk))
                    # Reset the bucket with the new topic's sentence
                    current_chunk = [sentences[i+1]]
                else:
                    # Same topic! Append the sentence string to the current bucket
                    current_chunk.append(sentences[i+1])
                    
            # Flush the final remaining sentences
            semantic_chunks.append(" ".join(current_chunk))
            return semantic_chunks, "LOCAL_SEMANTIC"
            
        except Exception as e:
            print(f"⚠️ Local semantic chunking failed: {e}. Falling back to recursive.")
            
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)
    return text_splitter.split_text(text), "RECURSIVE_FALLBACK"

# Execute with a relaxed threshold to group related sentences together
chunks, strategy = smart_chunker(document_text, use_semantic=True, similarity_threshold=0.25)

print(f"\n📊 Strategy used: 【 {strategy} 】")
for i, chunk in enumerate(chunks):
    print(f"Chunk {i+1}: {chunk}\n")      

# Save to file
output_file = "chunks_storage.json"
data_to_save = {
    "strategy_used": strategy,
    "total_chunks": len(chunks),
    "chunks": chunks
}

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(data_to_save, f, indent=4, ensure_ascii=False)

print(f"💾 Success! Saved {len(chunks)} chunks to '{os.path.abspath(output_file)}'")
