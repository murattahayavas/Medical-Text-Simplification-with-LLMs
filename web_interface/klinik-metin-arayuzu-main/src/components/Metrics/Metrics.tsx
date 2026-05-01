import { useRef, useEffect, useState } from 'react';
import { TrendingUp, Target, BookOpen, BarChart3 } from 'lucide-react';
import './Metrics.css';

interface CounterProps {
  end: number;
  decimals?: number;
  prefix?: string;
  suffix?: string;
  duration?: number;
  active: boolean;
}

const Counter = ({ end, decimals = 0, prefix = '', suffix = '', duration = 1800, active }: CounterProps) => {
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (!active) return;
    const startTime = performance.now();

    const tick = (now: number) => {
      const elapsed = now - startTime;
      const progress = Math.min(elapsed / duration, 1);
      // easeOutExpo
      const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      const current = eased * end;
      setValue(current);
      if (progress < 1) requestAnimationFrame(tick);
    };

    requestAnimationFrame(tick);
  }, [active, end, duration]);

  return (
    <span className="counter-value">
      {prefix}{value.toFixed(decimals)}{suffix}
    </span>
  );
};

const Metrics = () => {
  const sectionRef = useRef<HTMLDivElement>(null);
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold: 0.3 }
    );
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => observer.disconnect();
  }, []);

  return (
    <section id="metrics" className="metrics-section" ref={sectionRef}>
      <div className="container">
        <div className="section-header">
          <span className="section-label">Performans</span>
          <h2 className="section-title">Başarı ve Performans Metrikleri</h2>
          <p className="section-subtitle">
            Başarımız sadece "sadeleştirme" ile sınırlı değil, <strong>doğruluk odaklıdır</strong>.
          </p>
        </div>

        {/* Big Counter Cards */}
        <div className="metrics-counters">
          <div className="metric-counter-card">
            <div className="metric-counter-card__icon green">
              <TrendingUp size={24} />
            </div>
            <div className="metric-counter-card__numbers">
              <span className="metric-counter-card__before">0.17</span>
              <span className="metric-counter-card__arrow">→</span>
              <Counter end={0.79} decimals={2} active={visible} />
            </div>
            <span className="metric-counter-card__label">Başarı Puanı</span>
            <span className="metric-counter-card__desc">Baseline LLM vs. Agentic RAG + Reflexion</span>
          </div>

          <div className="metric-counter-card">
            <div className="metric-counter-card__icon blue">
              <Target size={24} />
            </div>
            <div className="metric-counter-card__numbers">
              <span className="metric-counter-card__prefix">~</span>
              <Counter end={300} decimals={0} suffix="%" active={visible} />
            </div>
            <span className="metric-counter-card__label">Tıbbi Doğruluk Artışı</span>
            <span className="metric-counter-card__desc">ICD-10 kodları korunma oranı</span>
          </div>

          <div className="metric-counter-card">
            <div className="metric-counter-card__icon purple">
              <BookOpen size={24} />
            </div>
            <div className="metric-counter-card__numbers">
              <Counter end={70} decimals={0} prefix=">" active={visible} />
            </div>
            <span className="metric-counter-card__label">Ateşman Hedef Skoru</span>
            <span className="metric-counter-card__desc">Okunabilirlik indeksi hedefi</span>
          </div>
        </div>

        {/* Metric Tags */}
        <div className="metrics-tag-bar">
          <span className="metrics-tag-bar__label">
            <BarChart3 size={16} />
            Ölçüm Metrikleri
          </span>
          <div className="metrics-tag-bar__tags">
            <span className="m-tag">Ateşman Okunabilirlik</span>
            <span className="m-tag">ICD-10 Doğruluğu</span>
            <span className="m-tag">BERTScore</span>
            <span className="m-tag">SARI</span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Metrics;
