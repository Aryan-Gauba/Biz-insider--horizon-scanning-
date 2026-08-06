// // import React, { useState, useEffect } from 'react';
// // import axios from 'axios';
// // import './App.css';

// // const EXPRESS_API = 'http://localhost:5000/api';

// // export default function App() {
// //   const [events, setEvents] = useState([]);
// //   const [metrics, setMetrics] = useState({ total_events: 0, impact_distribution: [] });
// //   const [loading, setLoading] = useState(true);
// //   const [searchQuery, setSearchQuery] = useState('');
// //   const [selectedImpact, setSelectedImpact] = useState('');

// //   useEffect(() => {
// //     fetchMetrics();
// //     fetchEvents();
// //   }, [selectedImpact]);

// //   const fetchMetrics = async () => {
// //     try {
// //       const res = await axios.get(`${EXPRESS_API}/metrics`);
// //       setMetrics(res.data);
// //     } catch (err) {
// //       console.error('Error fetching metrics:', err);
// //     }
// //   };

// //   const fetchEvents = async () => {
// //     setLoading(true);
// //     try {
// //       let url = `${EXPRESS_API}/events?limit=20`;
// //       if (selectedImpact) url += `&impact=${selectedImpact}`;
// //       const res = await axios.get(url);
// //       setEvents(res.data.data || []);
// //     } catch (err) {
// //       console.error('Error fetching events:', err);
// //     } finally {
// //       setLoading(false);
// //     }
// //   };

// //   const handleSearch = async (e) => {
// //     e.preventDefault();
// //     if (!searchQuery.trim()) {
// //       fetchEvents();
// //       return;
// //     }
// //     setLoading(true);
// //     try {
// //       const res = await axios.post(`${EXPRESS_API}/search`, { query: searchQuery });
// //       setEvents(res.data.results || []);
// //     } catch (err) {
// //       console.error('Error searching:', err);
// //     } finally {
// //       setLoading(false);
// //     }
// //   };

// //   return (
// //     <div className="dashboard-container">
// //       {/* Header */}
// //       <header className="dashboard-header">
// //         <div className="header-title">
// //           <h1>Horizon Scanning Intelligence</h1>
// //           <p>Macroeconomic Developments, Policy Risks & Vector Intelligence</p>
// //         </div>
// //         <div className="metric-badge">
// //           <span>Total Tracked Events</span>
// //           <strong>{metrics.total_events}</strong>
// //         </div>
// //       </header>

// //       {/* Control Bar */}
// //       <div className="controls-bar">
// //         <form onSubmit={handleSearch} className="search-form">
// //           <input
// //             type="text"
// //             className="search-input"
// //             value={searchQuery}
// //             onChange={(e) => setSearchQuery(e.target.value)}
// //             placeholder="Semantic query e.g. 'green energy tax incentives' or 'chip manufacturing'..."
// //           />
// //           <button type="submit" className="btn-primary">Search</button>
// //         </form>

// //         <div className="filter-group">
// //           <select
// //             className="filter-select"
// //             value={selectedImpact}
// //             onChange={(e) => setSelectedImpact(e.target.value)}
// //           >
// //             <option value="">All Impacts</option>
// //             <option value="POSITIVE">Positive Impact</option>
// //             <option value="NEGATIVE">Negative Impact</option>
// //             <option value="NEUTRAL">Neutral</option>
// //           </select>
// //           <button
// //             onClick={() => { setSearchQuery(''); setSelectedImpact(''); fetchEvents(); }}
// //             className="btn-secondary"
// //           >
// //             Reset
// //           </button>
// //         </div>
// //       </div>

// //       {/* Event Feed */}
// //       {loading ? (
// //         <div className="loading-state">Loading intelligence feed...</div>
// //       ) : events.length === 0 ? (
// //         <div className="empty-state">No policy or risk developments match your criteria.</div>
// //       ) : (
// //         <div className="events-feed">
// //           {events.map((evt) => (
// //             <div key={evt.id} className="event-card">
// //               <div className="card-header">
// //                 <a href={evt.source_url} target="_blank" rel="noopener noreferrer">
// //                   {evt.title}
// //                 </a>

// //                 {evt.impact_type === 'POSITIVE' && (
// //                   <span className="impact-tag positive">POSITIVE ({evt.impact_score})</span>
// //                 )}
// //                 {evt.impact_type === 'NEGATIVE' && (
// //                   <span className="impact-tag negative">NEGATIVE ({evt.impact_score})</span>
// //                 )}
// //                 {evt.impact_type === 'NEUTRAL' && (
// //                   <span className="impact-tag neutral">NEUTRAL</span>
// //                 )}
// //               </div>

// //               <p className="event-summary">{evt.summary}</p>

// //               {evt.impact_reasoning && (
// //                 <div className="explainability-block">
// //                   <strong>Impact Rationale & Explainability:</strong>
// //                   {evt.impact_reasoning}
// //                 </div>
// //               )}

// //               <div className="card-footer">
// //                 <span>Source: <strong style={{ color: '#e2e8f0' }}>{evt.source_name}</strong></span>
// //                 {evt.similarity_score && (
// //                   <span className="vector-score">
// //                     Vector Match: {(evt.similarity_score * 100).toFixed(1)}%
// //                   </span>
// //                 )}
// //               </div>
// //             </div>
// //           ))}
// //         </div>
// //       )}
// //     </div>
// //   );
// // }

// import React, { useState, useEffect } from 'react';
// import axios from 'axios';
// import './App.css';

// const EXPRESS_API = 'http://localhost:5000/api';

// export default function App() {
//   const [events, setEvents] = useState([]);
//   const [metrics, setMetrics] = useState({ total_events: 0, impact_distribution: [] });
//   const [loading, setLoading] = useState(true);
//   const [searchQuery, setSearchQuery] = useState('');
//   const [selectedImpact, setSelectedImpact] = useState('');

//   // Fetch metrics once on mount
//   useEffect(() => {
//     fetchMetrics();
//   }, []);

//   // Trigger search whenever the dropdown filter changes
//   useEffect(() => {
//     executeSearch();
//   }, [selectedImpact]);

//   const fetchMetrics = async () => {
//     try {
//       const res = await axios.get(`${EXPRESS_API}/metrics`);
//       setMetrics(res.data);
//     } catch (err) {
//       console.error('Error fetching metrics:', err);
//     }
//   };

//   // Single unified fetcher for both Search & Filtering
//   const executeSearch = async (e) => {
//     if (e) e.preventDefault();
//     setLoading(true);

//     try {
//       // If there is a text query, run Semantic Search with the selected impact filter
//       if (searchQuery.trim()) {
//         const res = await axios.post(`${EXPRESS_API}/search`, {
//           query: searchQuery,
//           impact: selectedImpact
//         });
//         setEvents(res.data.results || []);
//       } else {
//         // Otherwise, run standard database filter
//         let url = `${EXPRESS_API}/events?limit=20`;
//         if (selectedImpact) url += `&impact=${selectedImpact}`;
//         const res = await axios.get(url);
//         setEvents(res.data.data || []);
//       }
//     } catch (err) {
//       console.error('Error executing search/filter:', err);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleReset = () => {
//     setSearchQuery('');
//     setSelectedImpact('');
//     // Fetch default feeds
//     axios.get(`${EXPRESS_API}/events?limit=20`).then((res) => setEvents(res.data.data || []));
//   };

//   return (
//     <div className="dashboard-container">
//       {/* Header */}
//       <header className="dashboard-header">
//         <div className="header-title">
//           <h1>Horizon Scanning Intelligence</h1>
//           <p>Macroeconomic Developments, Policy Risks & Vector Intelligence</p>
//         </div>
//         <div className="metric-badge">
//           <span>Total Tracked Events</span>
//           <strong>{metrics.total_events}</strong>
//         </div>
//       </header>

//       {/* Control Bar */}
//       <div className="controls-bar">
//         <form onSubmit={executeSearch} className="search-form">
//           <input
//             type="text"
//             className="search-input"
//             value={searchQuery}
//             onChange={(e) => setSearchQuery(e.target.value)}
//             placeholder="Semantic query e.g. 'Chip manufacturing' or 'renewable energy'..."
//           />
//           <button type="submit" className="btn-primary">Search</button>
//         </form>

//         <div className="filter-group">
//           <select
//             className="filter-select"
//             value={selectedImpact}
//             onChange={(e) => setSelectedImpact(e.target.value)}
//           >
//             <option value="">All Impacts</option>
//             <option value="POSITIVE">Positive Impact</option>
//             <option value="NEGATIVE">Negative Impact</option>
//             <option value="NEUTRAL">Neutral</option>
//           </select>
//           <button onClick={handleReset} className="btn-secondary">Reset</button>
//         </div>
//       </div>

//       {/* Event Feed */}
//       {loading ? (
//         <div className="loading-state">Searching and filtering intelligence feed...</div>
//       ) : events.length === 0 ? (
//         <div className="empty-state">No developments match your search query and impact filter combination.</div>
//       ) : (
//         <div className="events-feed">
//           {events.map((evt) => (
//             <div key={evt.id} className="event-card">
//               <div className="card-header">
//                 <a href={evt.source_url} target="_blank" rel="noopener noreferrer">
//                   {evt.title}
//                 </a>

//                 {evt.impact_type === 'POSITIVE' && (
//                   <span className="impact-tag positive">POSITIVE ({evt.impact_score})</span>
//                 )}
//                 {evt.impact_type === 'NEGATIVE' && (
//                   <span className="impact-tag negative">NEGATIVE ({evt.impact_score})</span>
//                 )}
//                 {evt.impact_type === 'NEUTRAL' && (
//                   <span className="impact-tag neutral">NEUTRAL</span>
//                 )}
//               </div>

//               <p className="event-summary">{evt.summary}</p>

//               {evt.impact_reasoning && (
//                 <div className="explainability-block">
//                   <strong>Impact Rationale & Explainability:</strong>
//                   {evt.impact_reasoning}
//                 </div>
//               )}

//               <div className="card-footer">
//                 <span>Source: <strong style={{ color: '#e2e8f0' }}>{evt.source_name}</strong></span>
//                 {evt.similarity_score && (
//                   <span className="vector-score">
//                     Vector Match: {(evt.similarity_score * 100).toFixed(1)}%
//                   </span>
//                 )}
//               </div>
//             </div>
//           ))}
//         </div>
//       )}
//     </div>
//   );
// }

import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar'; // Adjust path if you put it in /pages
import LandingPage from './components/LandingPage';
import FeedView from './components/FeedView';
import TimelineView from './components/TimelineView';
import GraphView from './components/GraphView';
import './App.css';

const EXPRESS_API = 'http://localhost:5000/api';

export default function App() {
  return (
    <Router>
      <div className="app-wrapper">
        <Navbar />
        
        {/* Main Content Area */}
        <main className="dashboard-container" style={{ marginTop: '2rem' }}>
          <Routes>
            <Route path="/" element={<LandingPage />} />
            <Route path="/feed" element={<FeedView expressApi={EXPRESS_API} />} />
            <Route path="/timeline" element={<TimelineView expressApi={EXPRESS_API} />} />
            <Route path="/graph" element={<GraphView expressApi={EXPRESS_API} />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}