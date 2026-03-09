import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ChevronRight, ChevronLeft, Send, PlusCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const QuoteForm = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    nome: '', cognome: '', email: '', telefono: '',
    viaggiatori: 2, destinazioni: [''], dataInizio: '', durata: '',
    budget: '', tipologia: 'avventura', note: ''
  });

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleDestChange = (index: number, value: string) => {
    const newDest = [...formData.destinazioni];
    newDest[index] = value;
    setFormData({ ...formData, destinazioni: newDest });
  };

  const addDest = () => setFormData({ ...formData, destinazioni: [...formData.destinazioni, ''] });
  const nextStep = () => setStep(prev => prev + 1);
  const prevStep = () => setStep(prev => prev - 1);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    alert('Grazie! La tua richiesta è stata inviata con successo.');
    navigate('/');
  };

  const variants = {
    initial: { opacity: 0, x: 20 },
    animate: { opacity: 1, x: 0 },
    exit: { opacity: 0, x: -20 }
  };

  return (
    <div className="quote-page">
      <div className="modern-form-container">
        <div className="form-header">
          <h2>Richiedi il tuo Preventivo</h2>
          <p>Passaggio {step} di 3</p>
        </div>

        <div className="form-body">
          <form onSubmit={handleSubmit}>
            <AnimatePresence mode="wait">
              {step === 1 && (
                <motion.div key="step1" {...variants}>
                  <div className="grid-2">
                    <div className="form-group">
                      <label>Nome *</label>
                      <input type="text" name="nome" className="form-control" value={formData.nome} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                      <label>Cognome *</label>
                      <input type="text" name="cognome" className="form-control" value={formData.cognome} onChange={handleChange} required />
                    </div>
                  </div>
                  <div className="form-group">
                    <label>Email *</label>
                    <input type="email" name="email" className="form-control" value={formData.email} onChange={handleChange} required />
                  </div>
                  <div className="form-group">
                    <label>Telefono</label>
                    <input type="tel" name="telefono" className="form-control" value={formData.telefono} onChange={handleChange} />
                  </div>
                  <div style={{ textAlign: 'right', marginTop: '20px' }}>
                    <button type="button" className="btn btn-primary" onClick={nextStep}>Avanti</button>
                  </div>
                </motion.div>
              )}

              {step === 2 && (
                <motion.div key="step2" {...variants}>
                  {formData.destinazioni.map((dest, index) => (
                    <div className="form-group" key={index}>
                      <label>Destinazione {index + 1} *</label>
                      <input type="text" className="form-control" value={dest} onChange={(e) => handleDestChange(index, e.target.value)} required />
                    </div>
                  ))}
                  <button type="button" onClick={addDest} style={{ background: 'none', border: 'none', color: 'var(--primary-blue)', cursor: 'pointer', marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '5px' }}>
                    <PlusCircle size={16} /> Aggiungi destinazione
                  </button>

                  <div className="grid-2">
                    <div className="form-group">
                      <label>Data Inizio</label>
                      <input type="date" name="dataInizio" className="form-control" value={formData.dataInizio} onChange={handleChange} required />
                    </div>
                    <div className="form-group">
                      <label>Durata (giorni)</label>
                      <input type="number" name="durata" className="form-control" value={formData.durata} onChange={handleChange} required />
                    </div>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
                    <button type="button" className="btn" style={{ background: '#eee' }} onClick={prevStep}>Indietro</button>
                    <button type="button" className="btn btn-primary" onClick={nextStep}>Avanti</button>
                  </div>
                </motion.div>
              )}

              {step === 3 && (
                <motion.div key="step3" {...variants}>
                  <div className="form-group">
                    <label>Tipologia di Viaggio</label>
                    <select name="tipologia" className="form-control" value={formData.tipologia} onChange={handleChange}>
                      <option value="avventura">Avventura</option>
                      <option value="nozze">Viaggio di Nozze</option>
                      <option value="relax">Relax</option>
                      <option value="famiglia">Famiglia</option>
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Budget stimato a persona</label>
                    <input type="text" name="budget" className="form-control" placeholder="es. 3000€" value={formData.budget} onChange={handleChange} />
                  </div>
                  <div className="form-group">
                    <label>Note aggiuntive</label>
                    <textarea name="note" className="form-control" rows={4} value={formData.note} onChange={handleChange}></textarea>
                  </div>

                  <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '20px' }}>
                    <button type="button" className="btn" style={{ background: '#eee' }} onClick={prevStep}>Indietro</button>
                    <button type="submit" className="btn btn-primary">Invia Richiesta</button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </form>
        </div>
      </div>
    </div>
  );
};

export default QuoteForm;
