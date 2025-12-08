"""
Add KB article for "Not enrolled on selfcare portal" scenario
"""
import requests
import urllib3
from dotenv import load_dotenv
import os
from openai import OpenAI

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

# KB Article for "Not enrolled on selfcare"
kb_article = {
    "title": "How to reset password if not enrolled on Selfcare Portal",
    "text": """How to reset password if not enrolled on Selfcare Portal

Issue: Password reset when not enrolled on selfcare portal

If you are not enrolled on the Selfcare Portal, please follow these steps:

Step 1: Send an email to support@acecloudhosting.com

Step 2: In the email, mention:
- Your server username
- Request for password reset
- Ensure the email is authorized by your account owner

Step 3: Our support team will process your request and share an update once completed.

Alternative: You can also call our support team at 1-888-415-5240 (24/7) for immediate assistance.

Note: For faster password resets in the future, we recommend enrolling in the Selfcare Portal at https://selfcare.acecloudhosting.com"""
}

print("="*70)
print("Adding KB Article: Not Enrolled on Selfcare Portal")
print("="*70)

# Generate embedding
print("\nGenerating embedding...")
response = openai_client.embeddings.create(
    model=EMBEDDING_MODEL,
    input=kb_article["text"]
)
embedding = response.data[0].embedding

# Create vector ID
vector_id = "kb_not_enrolled_selfcare"

# Prepare vector
vector = {
    "id": vector_id,
    "values": embedding,
    "metadata": {
        "source": "kb_article",
        "title": kb_article["title"],
        "text": kb_article["text"]
    }
}

# Upsert to Pinecone
print(f"Upserting to Pinecone...")
upsert_response = requests.post(
    f"https://{INDEX_HOST}/vectors/upsert",
    headers=PINECONE_HEADERS,
    json={"vectors": [vector]},
    verify=False
)

if upsert_response.status_code == 200:
    print("✅ Successfully added KB article!")
    print(f"\nTitle: {kb_article['title']}")
    print(f"Vector ID: {vector_id}")
else:
    print(f"❌ Failed to add KB article: {upsert_response.status_code}")
    print(upsert_response.text)

# Verify by searching
print("\n" + "="*70)
print("Verifying by searching...")
print("="*70)

test_query = "not enrolled on selfcare"
response = openai_client.embeddings.create(
    model=EMBEDDING_MODEL,
    input=test_query
)
query_embedding = response.data[0].embedding

search_response = requests.post(
    f"https://{INDEX_HOST}/query",
    headers=PINECONE_HEADERS,
    json={
        "vector": query_embedding,
        "topK": 3,
        "includeMetadata": True,
        "filter": {"source": {"$eq": "kb_article"}}
    },
    verify=False
)

results = search_response.json().get('matches', [])
print(f"\nFound {len(results)} results for '{test_query}':")
for i, match in enumerate(results, 1):
    print(f"\n{i}. Score: {match['score']:.4f}")
    print(f"   Title: {match['metadata'].get('title', 'N/A')}")
    print(f"   Text preview: {match['metadata'].get('text', '')[:150]}...")

print("\n" + "="*70)
print("DONE!")
print("="*70)
