import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar';
import Footer from './components/Footer';
import Home from './pages/Home';
import QuoteForm from './pages/QuoteForm';
import './styles/main.css';

const GenericPage = ({ title }: { title: string }) => (
  <div style={{ marginTop: '80px', minHeight: '60vh' }}>
    <div style={{ background: 'var(--primary-blue)', color: 'white', padding: '100px 5%' }}>
      <h1>{title}</h1>
    </div>
    <div className="container" style={{ padding: '50px 0' }}>
      <p>Stiamo preparando i migliori contenuti per la pagina {title}. Torna a trovarci presto!</p>
    </div>
  </div>
);

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/destinazioni" element={<GenericPage title="Destinazioni" />} />
            <Route path="/idee-di-viaggio" element={<GenericPage title="Idee di Viaggio" />} />
            <Route path="/lista-nozze" element={<GenericPage title="Lista Nozze" />} />
            <Route path="/highlights" element={<GenericPage title="Highlights" />} />
            <Route path="/contatti" element={<GenericPage title="Contatti" />} />
            <Route path="/preventivo" element={<QuoteForm />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </Router>
  );
}

export default App;
