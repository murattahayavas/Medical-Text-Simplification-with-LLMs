import { HeartPulse, Code2 } from 'lucide-react';
import './Footer.css';

const footerLinks = [
  { label: 'Nasıl Çalışır', href: '#features' },
  { label: 'Araç', href: '#tool' },
  { label: 'Mimari', href: '#architecture' },
  { label: 'Metrikler', href: '#metrics' },
];

const Footer = () => {
  const handleClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    e.preventDefault();
    const el = document.querySelector(href);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <footer className="footer">
      <div className="footer-content">
        <div className="footer-left">
          <div className="footer-logo">
            <HeartPulse size={24} color="#2563eb" />
            Klinik<span>Sade</span>
          </div>
          <p className="footer-desc">Bu araç karmaşık tıbbi metinleri basitleştirmek amacıyla geliştirilmiştir.</p>
        </div>

        <div className="footer-nav">
          <span className="footer-nav__title">Hızlı Erişim</span>
          {footerLinks.map((link) => (
            <a key={link.href} href={link.href} className="footer-nav__link" onClick={(e) => handleClick(e, link.href)}>
              {link.label}
            </a>
          ))}
        </div>

        <div className="footer-right">
          <div className="footer-dev-badge">
            <Code2 size={18} color="#93c5fd" />
            Geliştiriciler: <span>...</span>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <span>© 2025 KlinikSade. Tüm hakları saklıdır.</span>
      </div>
    </footer>
  );
};

export default Footer;
