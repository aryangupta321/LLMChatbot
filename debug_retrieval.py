"""
Debug retrieval to see what's happening
"""
import requests
import json
from openai import OpenAI
from dotenv import load_dotenv
import os
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "support-chatbot"
EMBEDDING_MODEL = "text-embedding-3-small"

# Get index host
headers = {
    "Api-Key": PINECONE_API_KEY,
    "Content-Type": "application/json"
}

response = requests.get(
    "https://api.pinecone.io/indexes",
    headers=headers,
    verify=False
)
indexes = response.json()
INDEX_HOST = None
for idx in indexes.get('indexes', []):
    if idx['name'] == INDEX_NAME:
        INDEX_HOST = idx['host']
        break

PINECONE_HEADERS = {
    "Api-Key": PINECONE_API_KEY,
    "Content-Type": "application/json"
}

def test_retrieval(query):
    print(f"\n{'='*70}")
    print(f"QUERY: {query}")
    print(f"{'='*70}")
    
    # Expand short queries
    expanded_query = query
    if len(query.split()) <= 4:
        expanded_query = f"How to {query} in QuickBooks"
        print(f"Expanded to: {expanded_query}")
    
    # Generate embedding
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=expanded_query
    )
    query_embedding = response.data[0].embedding
    
    # Try KB articles first
    url = f"https://{INDEX_HOST}/query"
    kb_payload = {
        "vector": query_embedding,
        "topK": 5,
        "includeMetadata": True,
        "filter": {"source": {"$eq": "kb_article"}}
    }
    
    kb_response = requests.post(
        url,
        headers=PINECONE_HEADERS,
        json=kb_payload,
        verify=False
    )
    kb_results = kb_response.json().get('matches', [])
    
    print(f"\nKB Articles Found: {len(kb_results)}")
    for i, match in enumerate(kb_results[:3], 1):
        print(f"\n{i}. Score: {match['score']:.4f}")
        print(f"   Title: {match['metadata'].get('title', 'N/A')}")
        print(f"   Text: {match['metadata'].get('text', '')[:150]}...")
    
    # Check if good KB articles (>0.4)
    good_kb = [m for m in kb_results if m['score'] > 0.4]
    print(f"\nGood KB Articles (>0.4): {len(good_kb)}")
    
    return good_kb

# Test queries
test_retrieval("how to reset password")
test_retrieval("quickbooks frozen")
test_retrieval("reset password selfcare")
