import React, { useState } from 'react';
import { NavLink, Link } from 'react-router-dom';
import { Plane, Menu, X } from 'lucide-react';

const Navbar = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleMenu = () => setIsOpen(!isOpen);

  return (
    <nav className="navbar">
      <Link to="/" className="logo">
        <Plane size={28} />
        PROGETTO <span>VIAGGI</span>
      </Link>

      {/* Pulsante Hamburger per Mobile */}
      <div className="mobile-toggle" onClick={toggleMenu}>
        {isOpen ? <X size={28} /> : <Menu size={28} />}
      </div>

      {/* Menu Links */}
      <div className={`nav-links ${isOpen ? 'mobile-open' : ''}`}>
        <NavLink to="/" onClick={() => setIsOpen(false)} className={({ isActive }) => (isActive ? 'active' : '')}>Home</NavLink>
        <NavLink to="/destinazioni" onClick={() => setIsOpen(false)} className={({ isActive }) => (isActive ? 'active' : '')}>Destinazioni</NavLink>
        <NavLink to="/idee-di-viaggio" onClick={() => setIsOpen(false)} className={({ isActive }) => (isActive ? 'active' : '')}>Idee di Viaggio</NavLink>
        <NavLink to="/lista-nozze" onClick={() => setIsOpen(false)} className={({ isActive }) => (isActive ? 'active' : '')}>Lista Nozze</NavLink>
        <NavLink to="/highlights" onClick={() => setIsOpen(false)} className={({ isActive }) => (isActive ? 'active' : '')}>Highlights</NavLink>
        <NavLink to="/contatti" onClick={() => setIsOpen(false)} className={({ isActive }) => (isActive ? 'active' : '')}>Contatti</NavLink>
        <Link to="/preventivo" onClick={() => setIsOpen(false)} className="nav-cta">Richiedi Preventivo</Link>
      </div>
    </nav>
  );
};

export default Navbar;
