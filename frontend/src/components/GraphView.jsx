import React, { useEffect, useRef, useState } from 'react';
import axios from 'axios';
import { Network } from 'vis-network';

export default function GraphView({ expressApi }) {
  const containerRef = useRef(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get(`${expressApi}/graph`)
      .then((res) => {
        const { nodes, edges } = res.data;

        const formattedNodes = nodes.map(n => {
          let color = '#38bdf8'; // default blue
          if (n.group === 'COMPANY') color = '#a855f7'; // purple
          if (n.group === 'SECTOR') color = '#f59e0b'; // amber
          if (n.impact === 'POSITIVE') color = '#34d399'; // green
          if (n.impact === 'NEGATIVE') color = '#f87171'; // red

          return {
            id: n.id,
            label: n.label,
            color: { background: color, border: '#1e293b' },
            font: { color: '#ffffff', size: 12 }
          };
        });

        const formattedEdges = edges.map(e => ({
          from: e.from,
          to: e.to,
          label: e.label,
          font: { color: '#94a3b8', size: 9 },
          color: { color: '#1e293b' }
        }));

        const graphData = { nodes: formattedNodes, edges: formattedEdges };
        const options = {
          nodes: { shape: 'dot', size: 16 },
          physics: { barnesHut: { springLength: 120 } },
          height: '500px'
        };

        if (containerRef.current) {
          new Network(containerRef.current, graphData, options);
        }
      })
      .catch((err) => console.error('Error fetching graph:', err))
      .finally(() => setLoading(false));
  }, [expressApi]);

  return (
    <div>
      <header className="dashboard-header">
        <div className="header-title">
          <h1>Entity Relationship Graph</h1>
          <p>Interactive graph mapping events to companies and industrial sectors</p>
        </div>
      </header>

      {loading && <div className="loading-state">Loading relationship graph...</div>}
      
      <div 
        ref={containerRef} 
        style={{ 
          display: loading ? 'none' : 'block',
          backgroundColor: '#131b2e', 
          border: '1px solid #1e293b', 
          borderRadius: '12px' 
        }} 
      />
    </div>
  );
}