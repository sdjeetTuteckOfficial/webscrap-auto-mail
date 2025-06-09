import chromadb

# lazy initialize model, client, collection as globals inside functions
_model = None
_client = None
_collection = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
    return _model

def get_client_and_collection():
    global _client, _collection
    if _client is None or _collection is None:
        _client = chromadb.Client()
        _collection = _client.get_or_create_collection(name="roles")
    return _client, _collection

def embed_text(text):
    model = get_model()
    return model.encode(text).tolist()

def add_roles_from_excel(df):
    _, collection = get_client_and_collection()
    for idx, row in df.iterrows():
        collection.add(
            ids=[str(idx)],
            embeddings=[embed_text(row['Description'])],
            metadatas=[{"role": row['Role Name'], "url": row['Portfolio URL']}],
            documents=[row['Description']]
        )

def query_roles(job_description, top_k=3):
    _, collection = get_client_and_collection()
    query_emb = embed_text(job_description)
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)
    return results

