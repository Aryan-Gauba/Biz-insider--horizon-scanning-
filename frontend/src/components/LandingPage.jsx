import React from 'react';
import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="landing-container">
      <h1 className="landing-title">Horizon Scanning</h1>
      <p className="landing-subtitle">
        AI-powered vector intelligence platform. Monitor macroeconomic developments, 
        policy risks, and market sentiment in real-time.
      </p>
      <Link to="/feed" className="btn-launch">
        Launch Dashboard
      </Link>
    </div>
  );
}