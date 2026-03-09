import React from 'react';
import { Link } from 'react-router-dom';
import { Mail, Phone, MapPin } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div>
            <h4>Progetto Viaggi</h4>
            <p>Esperti nella creazione di viaggi su misura e liste nozze per l'Australia, la Nuova Zelanda e il Pacifico.</p>
            <p>Il tuo sogno inizia qui.</p>
          </div>
          <div>
            <h4>Esplora</h4>
            <Link to="/destinazioni">Destinazioni</Link>
            <Link to="/idee-di-viaggio">Idee di Viaggio</Link>
            <Link to="/lista-nozze">Lista Nozze</Link>
            <Link to="/preventivo">Richiedi un Preventivo</Link>
          </div>
          <div>
            <h4>Contatti</h4>
            <p><Phone size={16} style={{marginRight: '8px'}} /> +39 02 1234567</p>
            <p><Mail size={16} style={{marginRight: '8px'}} /> info@progettoviaggi.it</p>
            <p><MapPin size={16} style={{marginRight: '8px'}} /> Milano, Italia</p>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; {new Date().getFullYear()} Progetto Viaggi. Tutti i diritti riservati.</p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
