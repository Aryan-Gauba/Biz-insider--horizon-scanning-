import React, { useState, useEffect } from 'react';
import axios from 'axios';

export default function FeedView({ expressApi }) {
  const [events, setEvents] = useState([]);
  const [metrics, setMetrics] = useState({ total_events: 0 });
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedImpact, setSelectedImpact] = useState('');

  useEffect(() => {
    fetchMetrics();
    executeSearch();
  }, [selectedImpact]);

  const fetchMetrics = async () => {
    try {
      const res = await axios.get(`${expressApi}/metrics`);
      setMetrics(res.data);
    } catch (err) {
      console.error('Metrics Error:', err);
    }
  };

  const executeSearch = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    try {
      if (searchQuery.trim()) {
        const res = await axios.post(`${expressApi}/search`, {
          query: searchQuery,
          impact: selectedImpact
        });
        setEvents(res.data.results || []);
      } else {
        let url = `${expressApi}/events?limit=20`;
        if (selectedImpact) url += `&impact=${selectedImpact}`;
        const res = await axios.get(url);
        setEvents(res.data.data || []);
      }
    } catch (err) {
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <header className="dashboard-header">
        <div className="header-title">
          <h1>Live Intelligence Feed</h1>
          <p>Macroeconomic Developments & Policy Risks</p>
        </div>
        <div className="metric-badge">
          <span>Total Tracked Events</span>
          <strong>{metrics.total_events}</strong>
        </div>
      </header>

      <div className="controls-bar">
        <form onSubmit={executeSearch} className="search-form">
          <input
            type="text"
            className="search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Semantic query e.g. 'Renewable energy'..."
          />
          <button type="submit" className="btn-primary">Search</button>
        </form>

        <div className="filter-group">
          <select className="filter-select" value={selectedImpact} onChange={(e) => setSelectedImpact(e.target.value)}>
            <option value="">All Impacts</option>
            <option value="POSITIVE">Positive Impact</option>
            <option value="NEGATIVE">Negative Impact</option>
            <option value="NEUTRAL">Neutral</option>
          </select>
          <button onClick={() => { setSearchQuery(''); setSelectedImpact(''); executeSearch(); }} className="btn-secondary">
            Reset
          </button>
        </div>
      </div>

      {loading ? (
        <div className="loading-state">Loading intelligence feed...</div>
      ) : events.length === 0 ? (
        <div className="empty-state">No developments match your criteria.</div>
      ) : (
        <div className="events-feed">
          {events.map((evt) => (
            <div key={evt.id} className="event-card">
              <div className="card-header">
                <a href={evt.source_url} target="_blank" rel="noopener noreferrer">{evt.title}</a>
                {evt.impact_type === 'POSITIVE' && <span className="impact-tag positive">POSITIVE</span>}
                {evt.impact_type === 'NEGATIVE' && <span className="impact-tag negative">NEGATIVE</span>}
                {evt.impact_type === 'NEUTRAL' && <span className="impact-tag neutral">NEUTRAL</span>}
              </div>
              <p className="event-summary">{evt.summary}</p>
              {evt.impact_reasoning && (
                <div className="explainability-block">
                  <strong>Impact Rationale:</strong> {evt.impact_reasoning}
                </div>
              )}
              <div className="card-footer">
                <span>Source: <strong style={{ color: '#e2e8f0' }}>{evt.source_name}</strong></span>
                {evt.similarity_score && (
                  <span className="vector-score">Vector Match: {(evt.similarity_score * 100).toFixed(1)}%</span>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}