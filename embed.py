import chromadb
from sentence_transformers import SentenceTransformer

_model = None
_client = None
_collection = None

def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    return _model

def get_client_and_collection(collection_name="roles"):
    global _client, _collection
    if _client is None:
        _client = chromadb.Client()
    if _collection is None:
        _collection = _client.get_or_create_collection(name=collection_name)
    return _client, _collection

def embed_text(text):
    model = get_model()
    embedding = model.encode(text)
    return embedding.tolist()

def add_roles_from_excel(df):
    """
    Add roles from a pandas DataFrame to ChromaDB collection.
    Assumes df has columns 'Role Name', 'Description', 'Portfolio URL'.
    """
    _, collection = get_client_and_collection()
    for idx, row in df.iterrows():
        role_id = str(row.get('Role Name', idx))  # Prefer role name as ID if unique
        description = row.get('Description', '')
        portfolio_url = row.get('Portfolio URL', '')

        embedding = embed_text(description)

        # Check if this role_id already exists to avoid duplicates (optional)
        existing = collection.get(ids=[role_id])
        if existing['ids']:
            # Optionally update or skip
            continue

        collection.add(
            ids=[role_id],
            embeddings=[embedding],
            metadatas=[{"role": role_id, "url": portfolio_url}],
            documents=[description]
        )

def query_roles(job_description, top_k=3):
    """
    Query roles similar to job_description.
    Returns ChromaDB query result dict.
    """
    _, collection = get_client_and_collection()
    query_emb = embed_text(job_description)
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)
    return results
