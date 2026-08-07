# 🌐 CorporateIQ — Horizon Scanning Intelligence Engine

> A high-throughput, AI-driven macroeconomic intelligence platform that ingests real-time policy, business, and regulatory updates, computes enterprise risk sentiment, and provides real-time semantic vector search across financial entities.

![System Architecture](https://img.shields.io/badge/Architecture-Monorepo%20Serverless-blue)
![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20Vite%20%7C%20Tailwind-61DAFB)
![Backend](https://img.shields.io/badge/Backend-Node.js%20%7C%20Express-339933)
![AI Engine](https://img.shields.io/badge/AI%20Engine-FastAPI%20%7C%20PyTorch%20%7C%20HuggingFace-FF6F00)
![Database](https://img.shields.io/badge/Database-PostgreSQL%20%7C%20NeonDB-4169E1)

---

## 🚀 Key Features

* **Real-time Ingestion & Sentiment Analysis**: Ingests policy and financial updates via RSS feeds and news endpoints, applying financial NLP heuristics for impact scoring (`POSITIVE`, `NEGATIVE`, `NEUTRAL`).
* **Semantic Vector Search**: Computes 384-dimensional dense vector embeddings (`sentence-transformers/all-MiniLM-L6-v2`) to enable semantic concept matching (e.g., matching "renewable energy policy" to solar tariffs).
* **Enterprise Entity Graph**: Automatically extracts relationships between macro events, target corporate entities (e.g., Reliance, TCS, HDFC), and impacted industry sectors.
* **Timeline Trend Analytics**: Aggregates macro event sentiment and volume distribution over configurable time horizons.
* **Serverless Decoupled Micro-Architecture**: Engineered to run across isolated Vercel serverless deployments connected to a managed NeonDB instance.

---

## 🛠️ System Architecture
```
[ Local Machine / Ingestor ]
│
├──► (Ingestion Engine: RSS & News APIs)
└──► (NLP Processor Engine: Regex NER + Sentiment + Embeddings)
│
▼
[ NeonDB (PostgreSQL) ]
▲
│
[ FastAPI AI Service ] ◄── (Serverless Inference via Hugging Face)
▲
│
[ Node.js/Express Proxy API ]
▲
│
[ React / Vite Single Page App ]
```
## 📁 Repository Structure

```
Biz-insider/
├── ai_services/             # Python AI Engine & Vector Compute
│   ├── api.py              # FastAPI serverless entry point
│   ├── ingestion.py        # Multi-source RSS & NewsAPI ingestion pipeline
│   ├── processor.py        # NLP Entity Extraction, Sentiment & Vectorization
│   └── vercel.json         # Vercel configuration (@vercel/python)
│
├── backend/                 # Node.js API Proxy Gateway
│   ├── index.js            # Express server handling frontend proxy requests
│   └── vercel.json         # Vercel configuration (@vercel/node)
│
└── frontend/                # Single Page Application Frontend
    ├── src/                # React components (Feed, Timeline, Entity Graph)
    ├── vite.config.js      # Vite build pipeline
    └── vercel.json         # Vercel single-page app rewrite configuration
```

## 🚦 Local Setup & Installation
Prerequisites
<li>Node.js (v18+)
<li>Python (3.10+)
<li>NeonDB (PostgreSQL) Account

## ☁️ Production Deployment (Vercel)
The project is structured as 3 isolated Vercel deployments:
<li>biz-insider-ai: Root Directory ai_services (Uses @vercel/python).
<li>biz-insider-backend: Root Directory backend (Uses @vercel/node).
<li>biz-insider-frontend: Root Directory frontend (Uses Vite static build).

## Future Additions
The following future additions could be made:
<li>Making a Cron-Job logic to make the ingestion and processor scripts automatically at periodic intervals.
<li>Personalizing the events intelligent system to detect what the user does and shows relevant news/events on the top.
<li>For personalizing, adding an auth page for organizations or individuals to sign up/login.
