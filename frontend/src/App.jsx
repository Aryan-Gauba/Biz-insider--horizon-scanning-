
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar'; // Adjust path if you put it in /pages
import LandingPage from './components/LandingPage';
import FeedView from './components/FeedView';
import TimelineView from './components/TimelineView';
import GraphView from './components/GraphView';
import './App.css';

const EXPRESS_API = import.meta.env.VITE_EXPRESS_API || 'http://localhost:5000/api';

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