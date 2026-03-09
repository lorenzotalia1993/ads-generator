import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Swiper, SwiperSlide } from 'swiper/react';
import { Autoplay, EffectFade } from 'swiper/modules';
import { motion } from 'framer-motion';
import { Map, Compass, Camera, Heart, CheckCircle, Users } from 'lucide-react';

import 'swiper/css';
import 'swiper/css/effect-fade';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="w-full">
      {/* Hero Slider */}
      <section className="hero-slider">
        <Swiper
          modules={[Autoplay, EffectFade]}
          effect="fade"
          autoplay={{ delay: 5000 }}
          loop={true}
          className="h-full w-full"
        >
          <SwiperSlide>
            <div className="hero-slide" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1523482580672-f109ba8cb9be?q=80&w=1200&auto=format')" }}>
              <div className="hero-content">
                <h1>Scopri l'Australia</h1>
                <p>Itinerari su misura creati da chi l'Australia la vive davvero.</p>
                <button onClick={() => navigate('/preventivo')} className="btn btn-primary">Richiedi Preventivo</button>
              </div>
            </div>
          </SwiperSlide>
          <SwiperSlide>
            <div className="hero-slide" style={{ backgroundImage: "url('https://images.unsplash.com/photo-1469854523086-cc02fe5d8800?q=80&w=1200&auto=format')" }}>
              <div className="hero-content">
                <h1>Nuova Zelanda</h1>
                <p>Natura selvaggia e paesaggi mozzafiato per il tuo viaggio ideale.</p>
                <button onClick={() => navigate('/preventivo')} className="btn btn-primary">Scopri di Più</button>
              </div>
            </div>
          </SwiperSlide>
        </Swiper>
      </section>

      {/* Services icons grid */}
      <section className="services-container">
        <div className="services-grid">
          <div className="service-item" onClick={() => navigate('/destinazioni')}>
            <Map size={32} />
            <h4>Destinazioni</h4>
          </div>
          <div className="service-item" onClick={() => navigate('/idee-di-viaggio')}>
            <Compass size={32} />
            <h4>Idee Viaggio</h4>
          </div>
          <div className="service-item" onClick={() => navigate('/lista-nozze')}>
            <Heart size={32} />
            <h4>Lista Nozze</h4>
          </div>
          <div className="service-item" onClick={() => navigate('/highlights')}>
            <Camera size={32} />
            <h4>Highlights</h4>
          </div>
          <div className="service-item" onClick={() => navigate('/preventivo')}>
            <CheckCircle size={32} />
            <h4>Su Misura</h4>
          </div>
        </div>
      </section>

      {/* Intro Section */}
      <section className="container section-padding text-center">
        <h2 className="section-title">Viaggi Creati per Te</h2>
        <p className="section-subtitle">Dimentica i pacchetti turistici standard. Noi creiamo esperienze, non semplici viaggi.</p>
        
        <div className="card-grid">
          <div className="image-card" onClick={() => navigate('/preventivo')}>
            <img src="https://images.unsplash.com/photo-1510798831971-661eb04b3739?q=60&w=600&auto=format" alt="Nozze" />
            <div className="card-content">
              <h3>Viaggi di Nozze</h3>
            </div>
          </div>
          <div className="image-card" onClick={() => navigate('/preventivo')}>
            <img src="https://images.unsplash.com/photo-1533692328991-08159ff19fca?q=60&w=600&auto=format" alt="Avventura" />
            <div className="card-content">
              <h3>Avventura</h3>
            </div>
          </div>
          <div className="image-card" onClick={() => navigate('/preventivo')}>
            <img src="https://images.unsplash.com/photo-1511895426328-dc8714191300?q=60&w=600&auto=format" alt="Famiglia" />
            <div className="card-content">
              <h3>Famiglia</h3>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;
