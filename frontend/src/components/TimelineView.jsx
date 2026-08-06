import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, Legend } from 'recharts';

export default function TimelineView({ expressApi }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${expressApi}/timeline`)
      .then((res) => {
        setData(res.data.timeline || []);
      })
      .catch((err) => console.error('Error fetching timeline:', err))
      .finally(() => setLoading(false));
  }, [expressApi]);

  if (loading) {
    return <div className="loading-state">Loading interactive timeline...</div>;
  }

  if (data.length === 0) {
    return <div className="empty-state">No timeline event data available.</div>;
  }

  return (
    <div>
      <header className="dashboard-header">
        <div className="header-title">
          <h1>Event Density & Sentiment Timeline</h1>
          <p>Historical trend distribution of policy and market intelligence</p>
        </div>
      </header>

      <div className="event-card" style={{ padding: '2rem', height: '420px' }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
            <YAxis stroke="#94a3b8" fontSize={12} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#131b2e', 
                borderColor: '#1e293b', 
                color: '#f1f5f9',
                borderRadius: '8px'
              }} 
            />
            <Legend wrapperStyle={{ paddingTop: '10px' }} />
            <Area type="monotone" dataKey="positive_count" stackId="1" stroke="#34d399" fill="#064e3b" name="Positive Events" />
            <Area type="monotone" dataKey="negative_count" stackId="1" stroke="#f87171" fill="#881335" name="Negative Events" />
            <Area type="monotone" dataKey="neutral_count" stackId="1" stroke="#cbd5e1" fill="#334155" name="Neutral Events" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}