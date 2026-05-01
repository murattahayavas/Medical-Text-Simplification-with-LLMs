import { FileText, Activity, CheckCircle } from 'lucide-react';
import './Features.css';

const Features = () => {
  return (
    <section id="features" className="features-section">
      <div className="features-grid">
        <div className="feature-card">
          <div className="feature-icon blue">
            <FileText size={32} />
          </div>
          <h3 className="feature-title">1. Metni Girin</h3>
          <p className="feature-desc">Basitleştirmek istediğiniz tıbbi terimleri içeren orijinal klinik raporu sisteme yapıştırın.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon">
            <Activity size={32} />
          </div>
          <h3 className="feature-title">2. Yapay Zeka İşlesin</h3>
          <p className="feature-desc">Gelişmiş API altyapımız, tıbbi bağlamı kaybetmeden metni saniyeler içinde analiz eder.</p>
        </div>
        <div className="feature-card">
          <div className="feature-icon green">
            <CheckCircle size={32} />
          </div>
          <h3 className="feature-title">3. Sonucu Alın</h3>
          <p className="feature-desc">Hastalarınızla güvenle paylaşabileceğiniz, anlaşılır ve net sonuca anında ulaşın.</p>
        </div>
      </div>
    </section>
  );
};

export default Features;
