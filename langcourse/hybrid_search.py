from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain.retrievers import BM25Retriever
from langchain_core.retrievers import EnsembleRetriever 
from langchain_core.embeddings import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()

embeddings =OpenAIEmbeddings(model="text-embedding-3-small")

# document with semantic and specific identifiers 
documents = [
    Document(page_content="The cat sat on the mat. mat id = SFV1110 this mat is liked by the cats", metadata={"source": "doc1.txt"}),
    Document(page_content="The dog sat on the log.", metadata={"source": "doc2.txt"}),
    Document(page_content="The cat and dog sat together.", metadata={"source": "doc3.txt"}),
    Document(page_content="The quick brown fox jumps over the lazy dog.", metadata={"source":"doc4.txt"}),
    Document(page_content="The lazy dog was not happy.", metadata={"source":"doc5.txt"}),
]

vector_store = Chroma.from_documents(
    documents, embeddings, collection_name="hybrid_search_collection")


bm25_retriever = BM25Retriever.from_documents(
    documents,
    k=3
)

def test_query(query,  name, retriever):
    results = retriever.invoke(query)
    for i, doc in enumerate(results[:3]):
        preview = doc.page_content[:80] + "..."
        print(f"{name} {i + 1}: {preview}")
    return results
    
    
test_query = [
    'id = SFV1110',
]
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_store.as_retriever()],
    weights=[0.5, 0.5]
)

def hybrid_retrive(query,retriever,weights,k=3, rrf_k=60):
    results = retriever.invoke(query)
    print(f"Hybrid Retriever Results for query: '{query}'")
    for rank, doc in enumerate(results[:k]):
        preview = doc.page_content[:80] + "..."
        print(f"Rank {rank + 1}: {preview} (Source: {doc.metadata['source']})")
    return results


