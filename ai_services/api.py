import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
from huggingface_hub import InferenceClient

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
HF_TOKEN = os.getenv("HF_TOKEN")

app = FastAPI(
    title="Horizon Scanning Intelligence API",
    description="API for macroeconomic developments, impact scoring, and vector search",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Local Model Loader
local_embedder = None
try:
    from sentence_transformers import SentenceTransformer
    local_embedder = SentenceTransformer('all-MiniLM-L6-v2')
    print("Loaded local SentenceTransformer model.")
except Exception:
    print("SentenceTransformer not installed locally. Using Hugging Face client.")


def get_query_embedding(text: str) -> List[float]:
    """Generates embedding using local model or Hugging Face InferenceClient."""
    # Priority A: Local Model
    if local_embedder is not None:
        raw_emb = local_embedder.encode(text)
        if hasattr(raw_emb, "tolist"):
            raw_emb = raw_emb.tolist()
        arr = np.array(raw_emb)
        while arr.ndim > 1:
            arr = np.mean(arr, axis=0)
        return arr.tolist()

    # Priority B: Hugging Face Client (Uses updated HF router infrastructure)
    if not HF_TOKEN:
        raise ValueError("HF_TOKEN environment variable is missing in Vercel settings!")

    client = InferenceClient(api_key=HF_TOKEN)
    # Feature extraction call
    response = client.feature_extraction(
        text, 
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    arr = np.array(response)
    while arr.ndim > 1:
        arr = np.mean(arr, axis=0)

    return arr.tolist()


def cosine_similarity(v1, v2):
    """Calculates cosine similarity with strict float32 casting."""
    if v1 is None or v2 is None:
        return 0.0
        
    try:
        a = np.asarray(v1, dtype=np.float32).flatten()
        b = np.asarray(v2, dtype=np.float32).flatten()
        
        if a.shape[0] != b.shape[0]:
            print(f"[DIMENSION MISMATCH] Query Vector: {a.shape[0]} dims | DB Vector: {b.shape[0]} dims")
            return 0.0

        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
            
        return float(np.dot(a, b) / (norm_a * norm_b))
    except Exception as err:
        print(f"[Cosine Error] {err}")
        return 0.0


def get_db():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set!")
    return psycopg2.connect(DATABASE_URL)


@app.get("/")
def root():
    return {"status": "online", "message": "Horizon Scanning Intelligence API active!"}


# 1. Endpoint: Get Processed Events
@app.get("/api/events")
def get_events(
    sector: Optional[str] = None,
    impact: Optional[str] = None,
    limit: int = 20,
    offset: int = 0
):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT 
            p.id, r.title, r.source_name, r.source_url, r.published_at,
            p.summary, p.impact_type, p.impact_score, p.impact_reasoning,
            p.target_companies, p.target_sectors
        FROM processed_events p
        JOIN raw_events r ON p.raw_event_id = r.id
        WHERE 1=1
    """
    params = []

    if sector:
        query += " AND %s = ANY(p.target_sectors)"
        params.append(sector)
    if impact:
        query += " AND p.impact_type = %s"
        params.append(impact.upper())

    query += " ORDER BY r.ingested_at DESC LIMIT %s OFFSET %s;"
    params.extend([limit, offset])

    cur.execute(query, tuple(params))
    results = cur.fetchall()
    
    cur.close()
    conn.close()
    return {"count": len(results), "data": results}


# 2. Endpoint: Get Metrics
@app.get("/api/metrics")
def get_metrics():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    cur.execute("""
        SELECT impact_type, COUNT(*) as count 
        FROM processed_events 
        GROUP BY impact_type;
    """)
    impact_stats = cur.fetchall()

    cur.execute("SELECT COUNT(*) as total FROM processed_events;")
    total_events = cur.fetchone()["total"]

    cur.close()
    conn.close()

    return {
        "total_events": total_events,
        "impact_distribution": impact_stats
    }


# 3. Endpoint: Semantic Vector Search
@app.post("/api/search")
def semantic_search(query: str, impact: Optional[str] = None, top_k: int = 10):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    sql = """
        SELECT 
            p.id, r.title, r.source_name, r.source_url,
            p.summary, p.impact_type, p.impact_score, p.impact_reasoning,
            p.target_sectors, p.target_companies, p.embedding
        FROM processed_events p
        JOIN raw_events r ON p.raw_event_id = r.id
        WHERE 1=1
    """
    params = []

    if impact:
        sql += " AND p.impact_type = %s"
        params.append(impact.upper())

    cur.execute(sql, tuple(params))
    records = cur.fetchall()
    cur.close()
    conn.close()

    try:
        query_vector = get_query_embedding(query)

        scored_results = []
        for rec in records:
            emb = rec.pop("embedding", None)
            
            if emb is not None:
                sim = cosine_similarity(query_vector, emb)
                rec["similarity_score"] = round(sim, 4)
            else:
                rec["similarity_score"] = 0.0

            scored_results.append(rec)

        scored_results.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        return {"query": query, "impact_filter": impact, "results": scored_results[:top_k]}

    except Exception as err:
        print(f"[API ERROR] Semantic search vector calculation failed: {err}")
        for rec in records:
            rec.pop("embedding", None)
            rec["similarity_score"] = 0.0
            
        return {"query": query, "impact_filter": impact, "results": records[:top_k]}


# 4. Endpoint: Timeline Trends
@app.get("/api/timeline")
def get_timeline_data(days: int = 30):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    sql = """
        SELECT 
            DATE(r.published_at) as date,
            COUNT(*) as total_events,
            COUNT(CASE WHEN p.impact_type = 'POSITIVE' THEN 1 END) as positive_count,
            COUNT(CASE WHEN p.impact_type = 'NEGATIVE' THEN 1 END) as negative_count,
            COUNT(CASE WHEN p.impact_type = 'NEUTRAL' THEN 1 END) as neutral_count
        FROM processed_events p
        JOIN raw_events r ON p.raw_event_id = r.id
        WHERE r.published_at >= CURRENT_DATE - (INTERVAL '1 day' * %s)
        GROUP BY DATE(r.published_at)
        ORDER BY DATE(r.published_at) ASC;
    """
    cur.execute(sql, (days,))
    records = list(cur.fetchall())
    cur.close()
    conn.close()
    
    return {"timeline": records}


# 5. Endpoint: Entity Graph
@app.get("/api/graph")
def get_entity_graph(limit: int = 15):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    sql = """
        SELECT 
            p.id, r.title, p.impact_type, p.target_sectors, p.target_companies
        FROM processed_events p
        JOIN raw_events r ON p.raw_event_id = r.id
        ORDER BY r.published_at DESC
        LIMIT %s;
    """
    cur.execute(sql, (limit,))
    records = cur.fetchall()
    cur.close()
    conn.close()

    nodes = []
    edges = []
    node_set = set()

    for rec in records:
        event_node_id = f"evt_{rec['id']}"
        
        if event_node_id not in node_set:
            nodes.append({
                "id": event_node_id, 
                "label": rec['title'][:30] + "...", 
                "group": "EVENT", 
                "impact": rec['impact_type']
            })
            node_set.add(event_node_id)

        companies = rec['target_companies'] or []
        for comp in companies:
            comp_node_id = f"comp_{comp.lower().replace(' ', '_')}"
            if comp_node_id not in node_set:
                nodes.append({"id": comp_node_id, "label": comp, "group": "COMPANY"})
                node_set.add(comp_node_id)
            edges.append({"from": event_node_id, "to": comp_node_id, "label": "AFFECTS"})

        sectors = rec['target_sectors'] or []
        for sec in sectors:
            sec_node_id = f"sec_{sec.lower().replace(' ', '_')}"
            if sec_node_id not in node_set:
                nodes.append({"id": sec_node_id, "label": sec, "group": "SECTOR"})
                node_set.add(sec_node_id)
            edges.append({"from": event_node_id, "to": sec_node_id, "label": "BELONGS_TO"})

    return {"nodes": nodes, "edges": edges}