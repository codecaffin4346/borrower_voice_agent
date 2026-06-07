import database
import re
import math

# Common stopwords to filter out for basic TF-IDF / term overlap matching
STOPWORDS = set([
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "arent", "as", "at", 
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can", "cant", "cannot", 
    "co", "could", "couldnt", "did", "didnt", "do", "does", "doesnt", "doing", "dont", "down", "during", "each", 
    "few", "for", "from", "further", "had", "hadnt", "has", "hasnt", "have", "havent", "having", "he", "hed", 
    "hell", "hes", "her", "here", "heres", "hers", "herself", "him", "himself", "his", "how", "hows", "i", "id", 
    "ill", "im", "ive", "if", "in", "into", "is", "isnt", "it", "its", "itself", "lets", "me", "more", "most", 
    "mustnt", "my", "myself", "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought", 
    "our", "ours", "ourselves", "out", "over", "own", "same", "shant", "she", "shed", "shell", "shes", "should", 
    "shouldnt", "so", "some", "such", "than", "that", "thats", "the", "their", "theirs", "them", "themselves", 
    "then", "there", "theres", "these", "they", "theyd", "theyll", "theyre", "theyve", "this", "those", "through", 
    "to", "too", "under", "until", "up", "very", "was", "wasnt", "we", "wed", "well", "were", "weve", "werent", 
    "what", "whats", "when", "whens", "where", "wheres", "which", "while", "who", "whos", "whom", "why", "whys", 
    "with", "wont", "would", "wouldnt", "you", "youd", "youll", "youre", "youve", "your", "yours", "yourself", "yourselves"
])

def tokenize(text):
    """
    Cleans and tokenizes text.
    """
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    tokens = text.split()
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]

def calculate_cosine_similarity(query_tokens, doc_tokens):
    """
    Calculates simple term-frequency cosine similarity.
    """
    if not query_tokens or not doc_tokens:
        return 0.0
        
    # Build term counts
    q_counts = {}
    for t in query_tokens:
        q_counts[t] = q_counts.get(t, 0) + 1
        
    d_counts = {}
    for t in doc_tokens:
        d_counts[t] = d_counts.get(t, 0) + 1
        
    # Dot product
    dot_product = 0.0
    for term, val in q_counts.items():
        if term in d_counts:
            dot_product += val * d_counts[term]
            
    # Magnitudes
    q_magnitude = math.sqrt(sum(val ** 2 for val in q_counts.values()))
    d_magnitude = math.sqrt(sum(val ** 2 for val in d_counts.values()))
    
    if q_magnitude == 0 or d_magnitude == 0:
        return 0.0
        
    return dot_product / (q_magnitude * d_magnitude)

def retrieve_policy_documents(query: str, top_k: int = 3) -> list:
    """
    RAG Retrieval: Queries the database knowledge base, computes similarity scores,
    and returns the top_k relevant documents.
    """
    docs = database.get_kb_documents()
    query_tokens = tokenize(query)
    
    if not query_tokens:
        # Fallback to returning a default set if query is too short or empty
        return docs[:top_k]
        
    scored_docs = []
    for doc in docs:
        # Combine title and content for retrieval context
        doc_text = f"{doc['title']} {doc['content']}"
        doc_tokens = tokenize(doc_text)
        
        score = calculate_cosine_similarity(query_tokens, doc_tokens)
        
        # Add boost if query terms appear in the title
        title_tokens = tokenize(doc['title'])
        title_match_count = sum(1 for q in query_tokens if q in title_tokens)
        if title_match_count > 0:
            score += 0.2 * title_match_count
            
        scored_docs.append({
            "doc_id": doc["doc_id"],
            "title": doc["title"],
            "category": doc["category"],
            "content": doc["content"],
            "score": round(score, 4)
        })
        
    # Sort by score descending
    scored_docs.sort(key=lambda x: x["score"], reverse=True)
    
    # Filter out documents with zero similarity score unless top_k are forced
    hits = [d for d in scored_docs if d["score"] > 0]
    
    # Return top K
    return hits[:top_k] if hits else scored_docs[:top_k]
