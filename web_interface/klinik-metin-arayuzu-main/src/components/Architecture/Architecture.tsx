import { useState } from 'react';
import { Database, Network, FileText, Layers, Activity, RefreshCw } from 'lucide-react';
import './Architecture.css';

const tabs = [
  { id: 'data', label: 'Veri Katmanı', icon: Database },
  { id: 'pipeline', label: 'İşlem Hattı', icon: Layers },
  { id: 'reflexion', label: 'Reflexion', icon: RefreshCw },
];

const Architecture = () => {
  const [activeTab, setActiveTab] = useState('data');

  return (
    <section id="architecture" className="architecture-section">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-label">Sistem Mimarisi</span>
          <h2 className="section-title">Agentic RAG + Reflexion</h2>
          <p className="section-subtitle">
            Sadeleştirme sadece kelime değiştirmek değil, bilgi hiyerarşisini ve tıbbi özgünlüğü korumaktır.
          </p>
        </div>

        {/* Overview Card */}
        <div className="arch-overview">
          <div className="arch-overview__icon">
            <Network size={28} />
          </div>
          <p>
            Geleneksel doğrusal veri işleme hatları yerine, bu sistemde <strong>iteratif bir ajan döngüsü</strong> kullanılmaktadır. 
            Tüm bileşenler bağımsız çalışır ancak sürekli bir geri bildirim döngüsü ile birbirine bağlıdır. 
            Temel hedeflerimizden biri; doktorun teknik hassasiyetine (ICD-10 kodları) sadık kalarak, hastanın anlama ihtiyacı arasındaki <strong>semantik köprüyü</strong> güvenli bir şekilde kurmaktır.
          </p>
        </div>

        {/* Flow Diagram */}
        <div className="arch-diagram">
          <div className="diagram-node db-node">
            <Database size={22} />
            <span>FAISS Vektör DB</span>
            <small>(Cochrane Plains)</small>
          </div>

          <div className="diagram-connector vertical green-connector" />

          <div className="diagram-pipeline">
            <div className="diagram-node extract-node">
              <FileText size={22} />
              <span>Extraction Agent</span>
              <small>ICD-10 ve terimleri ayıklar</small>
            </div>

            <div className="diagram-connector horizontal" />

            <div className="diagram-node generate-node">
              <Layers size={22} />
              <span>Generation Agent</span>
              <small>5 farklı taslak metin üretir</small>
            </div>

            <div className="diagram-connector horizontal" />

            <div className="diagram-node evaluate-node">
              <Activity size={22} />
              <span>Evaluation Agent</span>
              <small>Okunabilirlik ve doğruluğu ölçer</small>
            </div>
          </div>

          <div className="diagram-loop-badge">
            <RefreshCw size={14} className="loop-spin" />
            <span>Reflexion Loop (Skor &lt; 0.70) — Eksik Kodları ve Hataları Düzeltir</span>
          </div>
        </div>

        {/* Tab Bar */}
        <div className="arch-tabs">
          <div className="arch-tabs__bar">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  className={`arch-tabs__btn ${activeTab === tab.id ? 'arch-tabs__btn--active' : ''}`}
                  onClick={() => setActiveTab(tab.id)}
                >
                  <Icon size={16} />
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Tab Content */}
          <div className="arch-tabs__content">
            {activeTab === 'data' && (
              <div className="arch-tab-panel">
                <h3>Veri Katmanı ve Dinamik RAG (FAISS)</h3>
                <p>
                  Sistemin bilgi temeli, tıbbi sadeleştirmede altın standart kabul edilen <strong>Cochrane Plain Language Summaries</strong> veri setine dayanır. 
                  Veriler <strong>FAISS</strong> indeksi üzerinden RAG mimarisine bağlanarak modele dinamik "few-shot" örnekleri sağlar ve tıbbi bağlamın korunmasına yardımcı olur.
                </p>
                <div className="arch-tab-panel__tags">
                  <span className="tech-tag">FAISS</span>
                  <span className="tech-tag">Cochrane</span>
                  <span className="tech-tag">RAG</span>
                  <span className="tech-tag">Few-Shot Learning</span>
                </div>
              </div>
            )}

            {activeTab === 'pipeline' && (
              <div className="arch-tab-panel">
                <h3>İşlem Hattı ve Ajan Yapısı</h3>
                <ul className="arch-agent-list">
                  <li>
                    <div className="agent-badge extract">Extraction</div>
                    <div>
                      <strong>Extraction Agent:</strong> Ham metinden ICD-10 kodlarını ve kritik teknik terimleri zorunlu korunacaklar olarak ayıklar.
                    </div>
                  </li>
                  <li>
                    <div className="agent-badge generate">Generation</div>
                    <div>
                      <strong>Generation Agent:</strong> Ayıklanan verilere ve RAG'dan gelen örneklere dayanarak 5 farklı taslak metin üretir.
                    </div>
                  </li>
                  <li>
                    <div className="agent-badge evaluate">Evaluation</div>
                    <div>
                      <strong>Evaluation Agent:</strong> Üretilen taslakları okunabilirlik (Ateşman) ve içerik bağlamında değerlendirir.
                    </div>
                  </li>
                </ul>
              </div>
            )}

            {activeTab === 'reflexion' && (
              <div className="arch-tab-panel">
                <h3>Öz-Düzenleme Döngüsü (Reflexion)</h3>
                <p>
                  Projeyi ayırt edici kılan ana mekanizmadır. Eğer değerlendirme skoru Ateşman eşik değerinin (<strong>0.70</strong>) altındaysa, 
                  sistem sözel geri bildirim üreterek metni yeniden iyileştirir. Ayrıca ilk üretimde kaybolabilen ICD kodları, 
                  bu döngü sayesinde "zorunlu kod yerleştirme" yönergesiyle metne hata yapmadan geri kazandırılır.
                </p>
                <div className="reflexion-detail">
                  <div className="reflexion-step">
                    <span className="step-num">1</span>
                    <span>Değerlendirme skoru hesaplanır</span>
                  </div>
                  <div className="reflexion-step">
                    <span className="step-num">2</span>
                    <span>Skor &lt; 0.70 ise sözel geri bildirim üretilir</span>
                  </div>
                  <div className="reflexion-step">
                    <span className="step-num">3</span>
                    <span>Eksik ICD kodları "zorunlu yerleştirme" ile geri kazandırılır</span>
                  </div>
                  <div className="reflexion-step">
                    <span className="step-num">4</span>
                    <span>Metin yeniden üretilir ve değerlendirilir</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
};

export default Architecture;
