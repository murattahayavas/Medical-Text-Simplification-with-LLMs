import { ArrowDown, HeartPulse } from 'lucide-react';
import './Hero.css';

interface HeroProps {
  onScrollToTool: () => void;
}

const Hero = ({ onScrollToTool }: HeroProps) => {
  return (
    <header className="hero-section">
      <div className="hero-pattern"></div>
      <div className="hero-content">
        <div className="hero-icon-wrapper">
          <HeartPulse size={48} color="#93c5fd" />
        </div>
        <h1 className="hero-title">
          Klinik Metinleri <span>Herkes İçin</span> Anlaşılır Kılın
        </h1>
        <p className="hero-subtitle">
          Sağlık profesyonellerinin hazırladığı karmaşık tıbbi raporları ve epikrizleri, hastaların kolayca anlayabileceği sade ve net bir dile saniyeler içinde çevirin.
        </p>
        <button onClick={onScrollToTool} className="btn-primary">
          Aracı Kullanmaya Başla
          <ArrowDown className="icon" size={24} />
        </button>
      </div>
    </header>
  );
};

export default Hero;
