const express = require('express');
const cors = require('cors');
const axios = require('axios');

const app = express();
const PORT = 5000;
const FASTAPI_URL = 'http://127.0.0.1:8000';

app.use(cors());
app.use(express.json());

// Proxy Endpoint 1: Fetch Metrics
app.get('/api/metrics', async (req, res) => {
    try {
        const response = await axios.get(`${FASTAPI_URL}/api/metrics`);
        res.json(response.data);
    } catch (error) {
        console.error('FastAPI Error:', error.message);
        res.status(500).json({ error: 'Failed to fetch metrics from AI engine' });
    }
});

// Proxy Endpoint 2: Fetch Filtered Events
app.get('/api/events', async (req, res) => {
    try {
        const { sector, impact, limit = 20 } = req.query;
        let url = `${FASTAPI_URL}/api/events?limit=${limit}`;
        if (sector) url += `&sector=${encodeURIComponent(sector)}`;
        if (impact) url += `&impact=${encodeURIComponent(impact)}`;

        const response = await axios.get(url);
        res.json(response.data);
    } catch (error) {
        console.error('FastAPI Error:', error.message);
        res.status(500).json({ error: 'Failed to fetch events from AI engine' });
    }
});

// Proxy Endpoint 3: Semantic Search
// app.post('/api/search', async (req, res) => {
//     try {
//         const { query, top_k = 10 } = req.body;
//         const response = await axios.post(
//             `${FASTAPI_URL}/api/search?query=${encodeURIComponent(query)}&top_k=${top_k}`
//         );
//         res.json(response.data);
//     } catch (error) {
//         console.error('FastAPI Error:', error.message);
//         res.status(500).json({ error: 'Failed to execute semantic search' });
//     }
// });

// Proxy Endpoint: Combined Semantic Search + Impact Filtering
app.post('/api/search', async (req, res) => {
    try {
        const { query, impact, top_k = 10 } = req.body;
        let url = `${FASTAPI_URL}/api/search?query=${encodeURIComponent(query)}&top_k=${top_k}`;
        
        if (impact) {
            url += `&impact=${encodeURIComponent(impact)}`;
        }

        const response = await axios.post(url);
        res.json(response.data);
    } catch (error) {
        console.error('FastAPI Error:', error.message);
        res.status(500).json({ error: 'Failed to execute semantic search' });
    }
});

// Proxy Endpoint: Timeline Data
app.get('/api/timeline', async (req, res) => {
    try {
        const response = await axios.get(`${FASTAPI_URL}/api/timeline`);
        res.json(response.data);
    } catch (error) {
        console.error('FastAPI Timeline Error:', error.message);
        res.status(500).json({ error: 'Failed to fetch timeline trends' });
    }
});

// Proxy Endpoint: Entity Graph
app.get('/api/graph', async (req, res) => {
    try {
        const response = await axios.get(`${FASTAPI_URL}/api/graph`);
        res.json(response.data);
    } catch (error) {
        console.error('FastAPI Graph Error:', error.message);
        res.status(500).json({ error: 'Failed to fetch relationship graph' });
    }
});

app.listen(PORT, () => {
    console.log(`Node Express Backend running on http://localhost:${PORT}`);
});