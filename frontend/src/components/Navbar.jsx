import React from 'react';
import { NavLink, Link } from 'react-router-dom';

export default function Navbar() {
  return (
    <nav className="navbar">
      <Link to="/" className="nav-brand">
        Corporate<span>IQ</span>
      </Link>
      <div className="nav-links">
        <NavLink to="/feed" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          Intelligence Feed
        </NavLink>
        <NavLink to="/timeline" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          Timeline
        </NavLink>
        <NavLink to="/graph" className={({ isActive }) => isActive ? "nav-link active" : "nav-link"}>
          Entity Graph
        </NavLink>
      </div>
    </nav>
  );
}