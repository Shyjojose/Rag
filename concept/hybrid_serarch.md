# hybrid search

vector search completely fail
-product codes 
    -no semantic meaning 
    -these are meaningless codes 
-Acronyms
    -wcag compliance might return document but vector dosent understand wcag
-Exact Names 
    -john smith accounting search 
    - people name family tree vector database the vector search find documents about accounting 
-error codes
    - if we pass in error code econ_refused 

TO mitigate has vector vs BM25 search 

---
vector search 
    semantic similarity synonyms natural quesitons 
    but bad at exact matches ,product codes, acronyms

BM25 search 
    Good at exact matches, rare items , codes and ids
    bad at synonyms and semantic meaning 

hybrid best of bothh 

query box -> split 
-vector search k=3 result a
- BM25 search result b

add result a and result b with reciprocal rank fusion rrf score = 1/(k+rank)
---

hybrid search when enterprise situation and legal documents 
q and a chatbot dosent need it 

--- 

# architecture 

vector retriver -> BM25 retriver -> ensemble retirver pass some weights 

prduction fusion methods 
Method A:
 Reciprocal Rank Fusion (RRF)This is the preferred standard if your vector database and BM25 engine output radically different score scales. RRF ignores the raw scores entirely and only looks at the position (rank) of the document in each list


 \(\text{RRF\ Score}=\sum _{m\in M}\frac{1}{k+\text{rank}_{m}(d)}\)\(M\): The set of retrieval systems (Vector and BM25).\(\text{rank}_m(d)\): The position of document \(d\) in system \(m\) (starting at 1).\(k\): A constant penalty parameter (usually set to 60 in production) to prevent top-ranked items from completely overwhelming slightly lower-ranked items.
Method B: Convex Combination (Weighted Scoring)
If your underlying vector database natively supports BM25 (like Milvus, Qdrant, or Pinecone V2), 
you can normalize both scores to a 0.0 - 1.0 range and apply a linear weight (\(\alpha \)):\(\text{Final\ Score}=(\alpha \times \text{Dense\ Score})+((1-\alpha )\times \text{Sparse\ Score})\)Legal/Compliance Search: Set \(\alpha = 0.3\) (heavily favoring BM25 exact wording matches).Conversational Chatbots: Set \(\alpha = 0.7\) (heavily favoring semantic intent).
-----
from langchain.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import Chroma

 // Initialize your parallel retrievals
vector_retriever = Chroma(...).as_retriever(search_kwargs={"k": 50})
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 50

// Ensemble with custom weights based on domain needs
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever], 
    weights=[0.4, 0.6] # 60% weight to exact BM25 matching for enterprise codes
)

------

# 1. Initialize your parallel retrievals
vector_retriever = Chroma(...).as_retriever(search_kwargs={"k": 50})
bm25_retriever = BM25Retriever.from_documents(documents)
bm25_retriever.k = 50

# 2. Ensemble with custom weights based on domain needs
ensemble_retriever = EnsembleRetriever(
    retrievers=[vector_retriever, bm25_retriever], 
    weights=[0.4, 0.6] # 60% weight to exact BM25 matching for enterprise codes
)
