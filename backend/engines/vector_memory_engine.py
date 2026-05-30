import chromadb

from sentence_transformers import SentenceTransformer

# =========================
# CHROMA CLIENT
# =========================

client = chromadb.PersistentClient(
    path="./chroma_memory"
)

collection = client.get_or_create_collection(
    name="dynexa_memory"
)

# =========================
# EMBEDDING MODEL
# =========================

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

# =========================
# MEMORY FILTER
# =========================

def should_store_memory(text):

    lowered = text.lower().strip()

    # =========================
    # IGNORE QUESTIONS
    # =========================

    if "?" in lowered:

        return False

    question_words = [

        "what",
        "which",
        "how",
        "why",
        "when",
        "where"
    ]

    if any(
        lowered.startswith(word)
        for word in question_words
    ):

        return False

    # =========================
    # IMPORTANT MEMORIES ONLY
    # =========================

    important_patterns = [

        "i am",
        "i am building",
        "my favorite",
        "i use",
        "i like",
        "i prefer",
        "my laptop",
        "my startup",
        "i work",
        "i build"
    ]

    return any(
        pattern in lowered
        for pattern in important_patterns
    )

# =========================
# STORE MEMORY
# =========================

def store_memory(text):

    if not should_store_memory(text):

        return

    embedding = embedding_model.encode(
        text
    ).tolist()

    memory_id = str(
        len(collection.get()["ids"]) + 1
    )

    collection.add(

        ids=[memory_id],

        embeddings=[embedding],

        documents=[text]
    )

# =========================
# SEARCH MEMORY
# =========================

def search_memory(query):

    embedding = embedding_model.encode(
        query
    ).tolist()

    results = collection.query(

        query_embeddings=[embedding],

        n_results=3
    )

    docs = results.get(
        "documents",
        [[]]
    )[0]

    distances = results.get(
        "distances",
        [[]]
    )[0]

    if not docs:

        return None

    filtered_docs = []

    for doc, distance in zip(
        docs,
        distances
    ):

        # =========================
        # STRONG SIMILARITY ONLY
        # =========================

        if distance < 1.0:

            filtered_docs.append(doc)

    if not filtered_docs:

        return None

    return filtered_docs[0]