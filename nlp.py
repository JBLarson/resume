from typing import List

def extract_keywords(text: str, top_n: int = 20) -> List[str]:
    """
    Call Gemini (or local embedding/TF-IDF) to
    rank the most salient terms.
    """
    # e.g. payload = {"prompt": "...", "maxTokens": ...}
    # parse response into List[str]
    return ["machine learning", "Python", "TensorFlow", ...]


def filter_and_rank(candidate_terms: List[str]) -> List[str]:
    """
    Remove duplicates, stopwords, enforce case/style.
    """
    return candidate_terms[:top_n]
