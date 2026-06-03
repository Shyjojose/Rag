import re
from typing import List, Tuple
from rank_bm25 import BM25Okapi


def simple_tokenize(text: str) -> List[str]:
    tokens = re.findall(r"\w+", text.lower())
    return tokens


def build_bm25_index(doc_texts: List[str]) -> Tuple[BM25Okapi, List[List[str]]]:
    """Builds a BM25 index from a list of document texts.

    Returns the BM25 object and the tokenized documents (needed for mapping results).
    """
    tokenized = [simple_tokenize(t) for t in doc_texts]
    bm25 = BM25Okapi(tokenized)
    return bm25, tokenized


def query_bm25(query: str, bm25: BM25Okapi, tokenized_docs: List[List[str]], top_n: int = 5):
    """Query BM25 index and return top_n (doc_index, score) tuples and raw texts.
    """
    q_tokens = simple_tokenize(query)
    scores = bm25.get_scores(q_tokens)
    ranked = sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    results = [(idx, float(score)) for idx, score in ranked[:top_n]]
    return results


if __name__ == "__main__":
    # Example usage
    docs = [
        "Error ECONNREFUSED occurred while connecting to server.",
        "Product code B08XWN256 is out of stock.",
        "John Smith - Accounting department, employee ID 12345.",
        "Accessibility guidelines: WCAG 2.1 conformance requirements.",
    ]

    bm25, tokenized = build_bm25_index(docs)

    queries = ["ECONNREFUSED", "B08XWN256", "WCAG", "John Smith accounting"]
    for q in queries:
        res = query_bm25(q, bm25, tokenized, top_n=3)
        print(f"\nQuery: {q}")
        for idx, score in res:
            print(f"  - Doc {idx} (score={score:.3f}): {docs[idx]}")
