# from fastapi import FastAPI, Query
# from fastapi.middleware.cors import CORSMiddleware
# import psycopg2
# from psycopg2.extras import RealDictCursor
# from sentence_transformers import SentenceTransformer
# import numpy as np
# from typing import Optional, List
# import os
# from dotenv import load_dotenv

# app = FastAPI(
#     title="Horizon Scanning Intelligence API",
#     description="API for macroeconomic developments, impact scoring, and vector search",
#     version="1.0.0"
# )

# # Enable CORS so your frontend (Node, React, etc.) can call this API without CORS errors
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # DB_CONFIG = {
# #     "dbname": "News_Events",
# #     "user": "postgres",
# #     "password": "12345",  # <-- Update with your PostgreSQL password
# #     "host": "localhost",
# #     "port": "5432"
# # }

# # Load environment variables from .env file
# load_dotenv()

# DATABASE_URL = os.getenv("DATABASE_URL")

# def get_db():
#     if not DATABASE_URL:
#         raise ValueError("DATABASE_URL environment variable is not set!")
#     return psycopg2.connect(DATABASE_URL)

# # Load lightweight embedding model for real-time vector search queries
# embedder = SentenceTransformer('all-MiniLM-L6-v2')


# def get_db():
#     return psycopg2.connect(**DB_CONFIG)


# def cosine_similarity(v1, v2):
#     """Calculate cosine similarity between two float vectors."""
#     a, b = np.array(v1), np.array(v2)
#     norm_product = np.linalg.norm(a) * np.linalg.norm(b)
#     if norm_product == 0:
#         return 0.0
#     return float(np.dot(a, b) / norm_product)


# @app.get("/")
# def root():
#     return {"status": "online", "message": "Horizon Scanning Intelligence API is active!"}


# # 1. Endpoint: Get Processed Events with Sector/Impact Filters
# @app.get("/api/events")
# def get_events(
#     sector: Optional[str] = None,
#     impact: Optional[str] = None,
#     limit: int = 20,
#     offset: int = 0
# ):
#     conn = get_db()
#     cur = conn.cursor(cursor_factory=RealDictCursor)
    
#     query = """
#         SELECT 
#             p.id, r.title, r.source_name, r.source_url, r.published_at,
#             p.summary, p.impact_type, p.impact_score, p.impact_reasoning,
#             p.target_companies, p.target_sectors
#         FROM processed_events p
#         JOIN raw_events r ON p.raw_event_id = r.id
#         WHERE 1=1
#     """
#     params = []

#     if sector:
#         query += " AND %s = ANY(p.target_sectors)"
#         params.append(sector)
#     if impact:
#         query += " AND p.impact_type = %s"
#         params.append(impact.upper())

#     query += " ORDER BY r.ingested_at DESC LIMIT %s OFFSET %s;"
#     params.extend([limit, offset])

#     cur.execute(query, tuple(params))
#     results = cur.fetchall()
    
#     cur.close()
#     conn.close()
#     return {"count": len(results), "data": results}


# # 2. Endpoint: Get Metrics for Frontend Charts & Visualizations
# @app.get("/api/metrics")
# def get_metrics():
#     conn = get_db()
#     cur = conn.cursor(cursor_factory=RealDictCursor)

#     # Impact Distribution
#     cur.execute("""
#         SELECT impact_type, COUNT(*) as count 
#         FROM processed_events 
#         GROUP BY impact_type;
#     """)
#     impact_stats = cur.fetchall()

#     # Total Events Count
#     cur.execute("SELECT COUNT(*) as total FROM processed_events;")
#     total_events = cur.fetchone()["total"]

#     cur.close()
#     conn.close()

#     return {
#         "total_events": total_events,
#         "impact_distribution": impact_stats
#     }


# # 3. Endpoint: Real-time Semantic Vector Search
# # @app.post("/api/search")
# # def semantic_search(query: str, top_k: int = 5):
#     query_vector = embedder.encode(query).tolist()

#     conn = get_db()
#     cur = conn.cursor(cursor_factory=RealDictCursor)

#     cur.execute("""
#         SELECT 
#             p.id, r.title, r.source_name, r.source_url,
#             p.summary, p.impact_type, p.impact_score, p.impact_reasoning,
#             p.target_sectors, p.target_companies, p.embedding
#         FROM processed_events p
#         JOIN raw_events r ON p.raw_event_id = r.id;
#     """)
#     records = cur.fetchall()
#     cur.close()
#     conn.close()

#     # Compute similarity against stored vector embeddings
#     scored_results = []
#     for rec in records:
#         emb = rec.pop("embedding")  # Exclude raw vector array from HTTP JSON output
#         if emb:
#             sim = cosine_similarity(query_vector, emb)
#             rec["similarity_score"] = round(sim, 4)
#             scored_results.append(rec)

#     scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
#     return {"query": query, "results": scored_results[:top_k]}

# # Updated Endpoint: Semantic Search with Impact Filtering
# @app.post("/api/search")
# def semantic_search(query: str, impact: Optional[str] = None, top_k: int = 10):
#     query_vector = embedder.encode(query).tolist()

#     conn = get_db()
#     cur = conn.cursor(cursor_factory=RealDictCursor)

#     # Base query
#     sql = """
#         SELECT 
#             p.id, r.title, r.source_name, r.source_url,
#             p.summary, p.impact_type, p.impact_score, p.impact_reasoning,
#             p.target_sectors, p.target_companies, p.embedding
#         FROM processed_events p
#         JOIN raw_events r ON p.raw_event_id = r.id
#         WHERE 1=1
#     """
#     params = []

#     # Apply impact filter directly inside SQL before calculating similarity
#     if impact:
#         sql += " AND p.impact_type = %s"
#         params.append(impact.upper())

#     cur.execute(sql, tuple(params))
#     records = cur.fetchall()
#     cur.close()
#     conn.close()

#     # Compute cosine similarity against filtered candidates
#     scored_results = []
#     for rec in records:
#         emb = rec.pop("embedding")
#         if emb:
#             sim = cosine_similarity(query_vector, emb)
#             rec["similarity_score"] = round(sim, 4)
#             scored_results.append(rec)

#     scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
#     return {"query": query, "impact_filter": impact, "results": scored_results[:top_k]}

# # 1. Timeline Trends Endpoint
# @app.get("/api/timeline")
# def get_timeline_data(days: int = 30):
#     conn = get_db()
#     cur = conn.cursor(cursor_factory=RealDictCursor)
    
#     # Aggregates event counts and sentiment breakdown grouped by date
#     sql = """
#         SELECT 
#             DATE(r.published_at) as date,
#             COUNT(*) as total_events,
#             COUNT(CASE WHEN p.impact_type = 'POSITIVE' THEN 1 END) as positive_count,
#             COUNT(CASE WHEN p.impact_type = 'NEGATIVE' THEN 1 END) as negative_count,
#             COUNT(CASE WHEN p.impact_type = 'NEUTRAL' THEN 1 END) as neutral_count
#         FROM processed_events p
#         JOIN raw_events r ON p.raw_event_id = r.id
#         WHERE r.published_at >= CURRENT_DATE - INTERVAL '%s days'
#         GROUP BY DATE(r.published_at)
#         ORDER BY DATE(r.published_at) ASC;
#     """
#     cur.execute(sql, (days,))
#     records = cur.fetchall()
#     cur.close()
#     conn.close()
    
#     return {"timeline": records}


# # 2. Entity Graph Endpoint (Nodes & Edges)
# @app.get("/api/graph")
# def get_entity_graph(limit: int = 15):
#     conn = get_db()
#     cur = conn.cursor(cursor_factory=RealDictCursor)
    
#     sql = """
#         SELECT 
#             p.id, r.title, p.impact_type, p.target_sectors, p.target_companies
#         FROM processed_events p
#         JOIN raw_events r ON p.raw_event_id = r.id
#         ORDER BY r.published_at DESC
#         LIMIT %s;
#     """
#     cur.execute(sql, (limit,))
#     records = cur.fetchall()
#     cur.close()
#     conn.close()

#     nodes = []
#     edges = []
#     node_set = set()

#     for rec in records:
#         event_node_id = f"evt_{rec['id']}"
        
#         # Event Node
#         if event_node_id not in node_set:
#             nodes.append({
#                 "id": event_node_id, 
#                 "label": rec['title'][:30] + "...", 
#                 "group": "EVENT", 
#                 "impact": rec['impact_type']
#             })
#             node_set.add(event_node_id)

#         # Company Nodes & Edges
#         companies = rec['target_companies'] or []
#         for comp in companies:
#             comp_node_id = f"comp_{comp.lower().replace(' ', '_')}"
#             if comp_node_id not in node_set:
#                 nodes.append({"id": comp_node_id, "label": comp, "group": "COMPANY"})
#                 node_set.add(comp_node_id)
#             edges.append({"from": event_node_id, "to": comp_node_id, "label": "AFFECTS"})

#         # Sector Nodes & Edges
#         sectors = rec['target_sectors'] or []
#         for sec in sectors:
#             sec_node_id = f"sec_{sec.lower().replace(' ', '_')}"
#             if sec_node_id not in node_set:
#                 nodes.append({"id": sec_node_id, "label": sec, "group": "SECTOR"})
#                 node_set.add(sec_node_id)
#             edges.append({"from": event_node_id, "to": sec_node_id, "label": "BELONGS_TO"})

#     return {"nodes": nodes, "edges": edges}

import os
from typing import List, Optional
from dotenv import load_dotenv
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

app = FastAPI(
    title="Horizon Scanning Intelligence API",
    description="API for macroeconomic developments, impact scoring, and vector search",
    version="1.0.0"
)

# Enable CORS so your frontend (Node, React, etc.) can call this API without CORS errors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set!")
    return psycopg2.connect(DATABASE_URL)


# Load lightweight embedding model for real-time vector search queries
embedder = SentenceTransformer('all-MiniLM-L6-v2')


def cosine_similarity(v1, v2):
    """Calculate cosine similarity between two float vectors."""
    a, b = np.array(v1), np.array(v2)
    norm_product = np.linalg.norm(a) * np.linalg.norm(b)
    if norm_product == 0:
        return 0.0
    return float(np.dot(a, b) / norm_product)


@app.get("/")
def root():
    return {"status": "online", "message": "Horizon Scanning Intelligence API is active!"}


# 1. Endpoint: Get Processed Events with Sector/Impact Filters
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


# 2. Endpoint: Get Metrics for Frontend Charts & Visualizations
@app.get("/api/metrics")
def get_metrics():
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Impact Distribution
    cur.execute("""
        SELECT impact_type, COUNT(*) as count 
        FROM processed_events 
        GROUP BY impact_type;
    """)
    impact_stats = cur.fetchall()

    # Total Events Count
    cur.execute("SELECT COUNT(*) as total FROM processed_events;")
    total_events = cur.fetchone()["total"]

    cur.close()
    conn.close()

    return {
        "total_events": total_events,
        "impact_distribution": impact_stats
    }


# 3. Endpoint: Semantic Search with Impact Filtering
@app.post("/api/search")
def semantic_search(query: str, impact: Optional[str] = None, top_k: int = 10):
    query_vector = embedder.encode(query).tolist()

    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Base query
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

    # Apply impact filter directly inside SQL before calculating similarity
    if impact:
        sql += " AND p.impact_type = %s"
        params.append(impact.upper())

    cur.execute(sql, tuple(params))
    records = cur.fetchall()
    cur.close()
    conn.close()

    # Compute cosine similarity against filtered candidates
    scored_results = []
    for rec in records:
        emb = rec.pop("embedding")
        if emb:
            sim = cosine_similarity(query_vector, emb)
            rec["similarity_score"] = round(sim, 4)
            scored_results.append(rec)

    scored_results.sort(key=lambda x: x["similarity_score"], reverse=True)
    return {"query": query, "impact_filter": impact, "results": scored_results[:top_k]}


# 4. Endpoint: Timeline Trends Endpoint
@app.get("/api/timeline")
def get_timeline_data(days: int = 30):
    conn = get_db()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Aggregates event counts and sentiment breakdown grouped by date
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
    records = cur.fetchall()
    cur.close()
    conn.close()
    
    return {"timeline": records}


# 5. Endpoint: Entity Graph Endpoint (Nodes & Edges)
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
        
        # Event Node
        if event_node_id not in node_set:
            nodes.append({
                "id": event_node_id, 
                "label": rec['title'][:30] + "...", 
                "group": "EVENT", 
                "impact": rec['impact_type']
            })
            node_set.add(event_node_id)

        # Company Nodes & Edges
        companies = rec['target_companies'] or []
        for comp in companies:
            comp_node_id = f"comp_{comp.lower().replace(' ', '_')}"
            if comp_node_id not in node_set:
                nodes.append({"id": comp_node_id, "label": comp, "group": "COMPANY"})
                node_set.add(comp_node_id)
            edges.append({"from": event_node_id, "to": comp_node_id, "label": "AFFECTS"})

        # Sector Nodes & Edges
        sectors = rec['target_sectors'] or []
        for sec in sectors:
            sec_node_id = f"sec_{sec.lower().replace(' ', '_')}"
            if sec_node_id not in node_set:
                nodes.append({"id": sec_node_id, "label": sec, "group": "SECTOR"})
                node_set.add(sec_node_id)
            edges.append({"from": event_node_id, "to": sec_node_id, "label": "BELONGS_TO"})

    return {"nodes": nodes, "edges": edges}