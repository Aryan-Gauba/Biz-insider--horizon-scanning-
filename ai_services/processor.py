
import logging
import json
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# 1. Load Environment Variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Helper function to obtain database connection
def get_db_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set!")
    return psycopg2.connect(DATABASE_URL)


# 2. Load Local Embedding Model (Free, Fast, Runs on CPU)
logging.info("Loading SentenceTransformer embedding model (all-MiniLM-L6-v2)...")
embedder = SentenceTransformer('all-MiniLM-L6-v2')


def fetch_pending_events(limit: int = 50):
    """Fetch raw events that haven't been processed yet."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
        SELECT r.id, r.title, r.summary, r.raw_content 
        FROM raw_events r
        LEFT JOIN processed_events p ON r.id = p.raw_event_id
        WHERE p.id IS NULL
        LIMIT %s;
    """
    cur.execute(query, (limit,))
    events = cur.fetchall()
    
    cur.close()
    conn.close()
    return events


def analyze_event_nlp(title: str, content: str):
    """
    NLP Entity & Impact Extraction Engine.
    Examines text for target sectors, company mentions, and estimates impact score.
    """
    full_text = f"{title} {content}".lower()
    
    # Sector Classification Heuristics
    sectors = []
    if any(k in full_text for k in ['bank', 'tax', 'rate', 'inflation', 'gdp', 'finance', 'budget', 'rbi']):
        sectors.append('Finance & Banking')
    if any(k in full_text for k in ['energy', 'oil', 'solar', 'green', 'petroleum', 'ev', 'hydrogen', 'fuel']):
        sectors.append('Energy & Utilities')
    if any(k in full_text for k in ['tech', 'ai', 'software', 'chip', 'cyber', 'data', 'digital']):
        sectors.append('Technology & Telecom')
    if any(k in full_text for k in ['trade', 'tariff', 'export', 'import', 'policy', 'regulation', 'government']):
        sectors.append('Policy & Governance')
        
    if not sectors:
        sectors.append('General Business')

    # Company Detection Heuristics
    companies = []
    company_keywords = {
        "Reliance Industries": ['reliance', 'jio', 'ril'],
        "Tata Consultancy Services": ['tcs', 'tata consultancy'],
        "HDFC Bank": ['hdfc'],
        "Infosys": ['infosys'],
        "Tata Motors": ['tata motors'],
        "Bharti Airtel": ['airtel']
    }
    for comp, keywords in company_keywords.items():
        if any(kw in full_text for kw in keywords):
            companies.append(comp)

    # Simple Sentiment & Business Impact Scoring (-1.0 to +1.0)
    pos_words = ['growth', 'profit', 'boost', 'surge', 'deal', 'expansion', 'tax cut', 'incentive', 'record', 'gain']
    neg_words = ['tariff', 'drop', 'decline', 'penalty', 'ban', 'crisis', 'inflation', 'risk', 'loss', 'fine', 'slump']

    pos_score = sum(1 for w in pos_words if w in full_text)
    neg_score = sum(1 for w in neg_words if w in full_text)

    if pos_score > neg_score:
        impact_type = 'POSITIVE'
        impact_score = round(min(0.2 + (pos_score * 0.15), 0.95), 2)
        reasoning = f"Regulatory or market trends indicate strategic upside for {', '.join(sectors)}."
    elif neg_score > pos_score:
        impact_type = 'NEGATIVE'
        impact_score = round(max(-0.2 - (neg_score * 0.15), -0.95), 2)
        reasoning = f"Potential policy friction, geopolitical risk, or cost pressures identified affecting {', '.join(sectors)}."
    else:
        impact_type = 'NEUTRAL'
        impact_score = 0.0
        reasoning = "Informational news event with neutral direct financial impact."

    return {
        "summary": content[:300] + "..." if len(content) > 300 else content,
        "impact_type": impact_type,
        "impact_score": impact_score,
        "impact_reasoning": reasoning,
        "target_sectors": sectors,
        "target_companies": companies if companies else ["General Market"]
    }


def process_and_store():
    pending_events = fetch_pending_events(limit=100)
    if not pending_events:
        logging.info("All raw events are already processed!")
        return

    logging.info(f"Processing {len(pending_events)} pending raw events...")
    
    conn = get_db_connection()
    cur = conn.cursor()

    insert_query = """
        INSERT INTO processed_events 
        (raw_event_id, summary, impact_type, impact_score, impact_reasoning, target_companies, target_sectors, embedding)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
    """

    for idx, event in enumerate(pending_events):
        raw_id = event['id']
        title = event['title']
        content = event['summary'] or event['raw_content'] or title

        # 1. Extract NLP Insights
        insights = analyze_event_nlp(title, content)

        # 2. Create 384-dimensional Embedding
        text_to_embed = f"{title}: {content}"
        embedding = embedder.encode(text_to_embed).tolist()

        # 3. Store in Postgres
        cur.execute(insert_query, (
            raw_id,
            insights['summary'],
            insights['impact_type'],
            insights['impact_score'],
            insights['impact_reasoning'],
            insights['target_companies'],
            insights['target_sectors'],
            embedding
        ))

    conn.commit()
    cur.close()
    conn.close()
    logging.info(f"Batch completed! Successfully processed and stored vector embeddings for {len(pending_events)} events.")


if __name__ == "__main__":
    process_and_store()