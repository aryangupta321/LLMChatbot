"""
Remove all chat transcripts from Pinecone, keep only KB articles.
This will make retrieval cleaner and more predictable.
"""
import requests
import urllib3
from dotenv import load_dotenv
import os
import time

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
INDEX_NAME = "support-chatbot"

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

print(f"Index Host: {INDEX_HOST}")

PINECONE_HEADERS = {
    "Api-Key": PINECONE_API_KEY,
    "Content-Type": "application/json"
}

# Step 1: Get current stats
print("\n" + "="*70)
print("STEP 1: Current Pinecone Stats")
print("="*70)

stats_response = requests.post(
    f"https://{INDEX_HOST}/describe_index_stats",
    headers=PINECONE_HEADERS,
    json={},
    verify=False
)
stats = stats_response.json()
print(f"Total vectors: {stats['totalVectorCount']}")
print(f"Namespaces: {stats.get('namespaces', {})}")

# Step 2: Delete all chat transcripts
print("\n" + "="*70)
print("STEP 2: Deleting Chat Transcripts")
print("="*70)

delete_payload = {
    "filter": {
        "source": {"$eq": "chat_transcript"}
    },
    "deleteAll": False
}

print("Sending delete request...")
delete_response = requests.post(
    f"https://{INDEX_HOST}/vectors/delete",
    headers=PINECONE_HEADERS,
    json=delete_payload,
    verify=False
)

if delete_response.status_code == 200:
    print("✅ Delete request successful")
else:
    print(f"❌ Delete failed: {delete_response.status_code}")
    print(delete_response.text)
    exit(1)

# Wait for deletion to complete
print("\nWaiting 10 seconds for deletion to complete...")
time.sleep(10)

# Step 3: Verify deletion
print("\n" + "="*70)
print("STEP 3: Verifying Deletion")
print("="*70)

stats_response = requests.post(
    f"https://{INDEX_HOST}/describe_index_stats",
    headers=PINECONE_HEADERS,
    json={},
    verify=False
)
stats = stats_response.json()
print(f"Total vectors after deletion: {stats['totalVectorCount']}")

# Step 4: Query to confirm only KB articles remain
print("\n" + "="*70)
print("STEP 4: Confirming Only KB Articles Remain")
print("="*70)

# Try to find any chat transcripts
from openai import OpenAI
openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

test_query = "password reset"
response = openai_client.embeddings.create(
    model="text-embedding-3-small",
    input=test_query
)
query_embedding = response.data[0].embedding

# Search for chat transcripts
chat_search = requests.post(
    f"https://{INDEX_HOST}/query",
    headers=PINECONE_HEADERS,
    json={
        "vector": query_embedding,
        "topK": 5,
        "includeMetadata": True,
        "filter": {"source": {"$eq": "chat_transcript"}}
    },
    verify=False
)
chat_results = chat_search.json().get('matches', [])
print(f"Chat transcripts found: {len(chat_results)}")

# Search for KB articles
kb_search = requests.post(
    f"https://{INDEX_HOST}/query",
    headers=PINECONE_HEADERS,
    json={
        "vector": query_embedding,
        "topK": 5,
        "includeMetadata": True,
        "filter": {"source": {"$eq": "kb_article"}}
    },
    verify=False
)
kb_results = kb_search.json().get('matches', [])
print(f"KB articles found: {len(kb_results)}")

if len(chat_results) == 0 and len(kb_results) > 0:
    print("\n✅ SUCCESS! Only KB articles remain in Pinecone.")
    print(f"   Total KB articles: {stats['totalVectorCount']}")
else:
    print("\n⚠️ WARNING: Still found chat transcripts or no KB articles found")

print("\n" + "="*70)
print("CLEANUP COMPLETE")
print("="*70)
print("\nNext steps:")
print("1. Test the bot locally to ensure it still works")
print("2. Deploy to Railway")
print("3. Monitor responses - they should be cleaner and more consistent")
