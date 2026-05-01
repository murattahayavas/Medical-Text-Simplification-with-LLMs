import { useState, useEffect, useRef, forwardRef } from 'react';
import { FileText, CheckCircle, Copy, Activity, Upload, X, Download, Type, FileUp } from 'lucide-react';
import * as pdfjsLib from 'pdfjs-dist';
import { jsPDF } from 'jspdf';
import './SimplifierTool.css';

// PDF.js worker — CDN
pdfjsLib.GlobalWorkerOptions.workerSrc = `https://cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.mjs`;

interface SimplifierToolProps {
  onShowToast: (message: string, type?: 'success' | 'error') => void;
}

type InputMode = 'text' | 'pdf';

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

const SimplifierTool = forwardRef<HTMLDivElement, SimplifierToolProps>(({ onShowToast }, ref) => {
  const [inputText, setInputText] = useState('');
  const [outputText, setOutputText] = useState('');
  const [displayedText, setDisplayedText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [inputMode, setInputMode] = useState<InputMode>('text');
  const [pdfFile, setPdfFile] = useState<{ name: string; pages: number } | null>(null);
  const [isPdfLoading, setIsPdfLoading] = useState(false);
  const [isDragOver, setIsDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const API_URL = import.meta.env.VITE_API_URL as string | undefined;

  // Typewriter effect
  useEffect(() => {
    if (!outputText) {
      setDisplayedText('');
      return;
    }
    let currentIndex = 0;
    const intervalId = setInterval(() => {
      setDisplayedText(outputText.slice(0, currentIndex + 1));
      currentIndex++;
      if (currentIndex === outputText.length) clearInterval(intervalId);
    }, 15);
    return () => clearInterval(intervalId);
  }, [outputText]);

  // ── PDF Text Extract ──
  const extractTextFromPdf = async (file: File) => {
    if (file.size > MAX_FILE_SIZE) {
      onShowToast('PDF dosyası 10MB limitini aşıyor.', 'error');
      return;
    }
    setIsPdfLoading(true);
    try {
      const arrayBuffer = await file.arrayBuffer();
      const pdf = await pdfjsLib.getDocument({ data: arrayBuffer }).promise;
      let fullText = '';
      for (let i = 1; i <= pdf.numPages; i++) {
        const page = await pdf.getPage(i);
        const content = await page.getTextContent();
        const pageText = content.items
          .map((item: any) => item.str)
          .join(' ');
        fullText += pageText + '\n\n';
      }
      setInputText(fullText.trim());
      setPdfFile({ name: file.name, pages: pdf.numPages });
      onShowToast(`"${file.name}" başarıyla yüklendi (${pdf.numPages} sayfa).`, 'success');
    } catch (err) {
      console.error('PDF okuma hatası:', err);
      onShowToast('PDF dosyası okunamadı. Lütfen geçerli bir PDF yükleyin.', 'error');
    } finally {
      setIsPdfLoading(false);
    }
  };

  // ── Drag & Drop ──
  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(true);
  };
  const handleDragLeave = () => setIsDragOver(false);
  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file?.type === 'application/pdf') {
      extractTextFromPdf(file);
    } else {
      onShowToast('Sadece PDF dosyaları desteklenmektedir.', 'error');
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) extractTextFromPdf(file);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const clearPdf = () => {
    setPdfFile(null);
    setInputText('');
  };

  // ── API Call ──
  const handleSimplify = async () => {
    if (!inputText.trim()) return;
    setIsLoading(true);
    setOutputText('');
    setDisplayedText('');

    try {
      if (API_URL) {
        const response = await fetch(API_URL, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: inputText }),
        });
        if (!response.ok) throw new Error('API isteği başarısız oldu.');
        const data = await response.json();
        setOutputText(data.simplified || data.result || data.text || "Sunucudan dönen metin burada.");
      } else {
        console.warn('VITE_API_URL tanımlanmadı. Mock veri kullanılıyor.');
        await new Promise(resolve => setTimeout(resolve, 1500));
        setOutputText("Bu alan, arka planda API'nizden gelen basitleştirilmiş klinik metni gösterir.\n\nSimüle edilen örnek dönüştürme:\n'Miyokard enfarktüsü' -> 'Kalp krizi'\n'Hipertansiyon' -> 'Yüksek tansiyon'\n\nGerçek API'nizi bağlamak için '.env' dosyası oluşturup VITE_API_URL değişkenini ayarlayınız.");
      }
    } catch (error: any) {
      console.error("API Hatası:", error);
      onShowToast(error.message || 'Sunucuya bağlanırken bir hata oluştu.', 'error');
      setOutputText('İşlem sırasında bir hata oluştu. Lütfen bağlantınızı ve API ayarlarınızı kontrol edin.');
    } finally {
      setIsLoading(false);
    }
  };

  // ── Copy ──
  const handleCopy = () => {
    if (displayedText) {
      navigator.clipboard.writeText(displayedText);
      onShowToast('Metin kopyalandı!', 'success');
    }
  };

  // ── PDF Download ──
  const handleDownloadPdf = () => {
    if (!displayedText) return;
    try {
      const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' });

      // Title
      doc.setFontSize(18);
      doc.setFont('helvetica', 'bold');
      doc.text('Basitlestirilmis Klinik Rapor', 20, 25);

      // Date
      doc.setFontSize(9);
      doc.setFont('helvetica', 'normal');
      doc.setTextColor(120);
      doc.text(`Olusturulma Tarihi: ${new Date().toLocaleDateString('tr-TR')}`, 20, 33);

      // Divider
      doc.setDrawColor(200);
      doc.line(20, 36, 190, 36);

      // Body
      doc.setFontSize(11);
      doc.setTextColor(40);
      doc.setFont('helvetica', 'normal');

      const lines = doc.splitTextToSize(displayedText, 170);
      let y = 44;
      const pageHeight = 280;

      for (const line of lines) {
        if (y > pageHeight) {
          doc.addPage();
          y = 20;
        }
        doc.text(line, 20, y);
        y += 6;
      }

      // Footer
      const pageCount = doc.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(160);
        doc.text('KlinikSade - Klinik Metin Basitlestirme Araci', 20, 290);
        doc.text(`Sayfa ${i} / ${pageCount}`, 175, 290);
      }

      doc.save('basitlestirilmis-rapor.pdf');
      onShowToast('PDF başarıyla indirildi!', 'success');
    } catch (err) {
      console.error('PDF oluşturma hatası:', err);
      onShowToast('PDF oluşturulurken bir hata oluştu.', 'error');
    }
  };

  const isOutputReady = displayedText && displayedText.length === outputText.length;

  return (
    <main ref={ref} id="tool" className="tool-section">
      <div className="container">
        {/* Section Header */}
        <div className="section-header">
          <span className="section-label">Araç</span>
          <h2 className="section-title">Metin Basitleştirici</h2>
          <p className="section-subtitle">
            Karmaşık tıbbi metni yapıştırın veya PDF olarak yükleyin — yapay zeka saniyeler içinde sadeleştirsin.
          </p>
        </div>

        <div className="panels-container">
          {/* ── Input Panel ── */}
          <div className="panel">
            <div className="panel-header">
              <span className="panel-title blue-icon">
                <FileText size={18} />
                Orijinal Klinik Metin
              </span>
              {/* Input Mode Toggle */}
              <div className="input-toggle">
                <button
                  className={`input-toggle__btn ${inputMode === 'text' ? 'input-toggle__btn--active' : ''}`}
                  onClick={() => setInputMode('text')}
                >
                  <Type size={14} /> Metin
                </button>
                <button
                  className={`input-toggle__btn ${inputMode === 'pdf' ? 'input-toggle__btn--active' : ''}`}
                  onClick={() => setInputMode('pdf')}
                >
                  <FileUp size={14} /> PDF
                </button>
              </div>
            </div>

            {inputMode === 'text' ? (
              <textarea
                className="panel-textarea"
                placeholder="Örn: Hasta acil servise retrosternal göğüs ağrısı şikayeti ile başvurdu. EKG'sinde akut anterior miyokard enfarktüsü bulguları izlendi..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
            ) : (
              <div className="pdf-input-area">
                {!pdfFile ? (
                  <div
                    className={`dropzone ${isDragOver ? 'dropzone--active' : ''} ${isPdfLoading ? 'dropzone--loading' : ''}`}
                    onDragOver={handleDragOver}
                    onDragLeave={handleDragLeave}
                    onDrop={handleDrop}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".pdf"
                      onChange={handleFileSelect}
                      className="dropzone__input"
                    />
                    {isPdfLoading ? (
                      <>
                        <Activity className="animate-spin dropzone__icon" size={32} />
                        <span className="dropzone__text">PDF okunuyor...</span>
                      </>
                    ) : (
                      <>
                        <Upload className="dropzone__icon" size={32} />
                        <span className="dropzone__text">PDF dosyanızı sürükleyip bırakın</span>
                        <span className="dropzone__hint">veya buraya tıklayarak seçin (Maks. 10MB)</span>
                      </>
                    )}
                  </div>
                ) : (
                  <div className="pdf-loaded">
                    <div className="pdf-loaded__info">
                      <FileText size={20} className="pdf-loaded__icon" />
                      <div>
                        <span className="pdf-loaded__name">{pdfFile.name}</span>
                        <span className="pdf-loaded__pages">{pdfFile.pages} sayfa — metin ayıklandı</span>
                      </div>
                    </div>
                    <button className="pdf-loaded__clear" onClick={clearPdf} title="PDF'i Kaldır">
                      <X size={16} />
                    </button>
                  </div>
                )}

                {/* Extracted text preview */}
                {pdfFile && inputText && (
                  <textarea
                    className="panel-textarea pdf-preview"
                    value={inputText}
                    onChange={(e) => setInputText(e.target.value)}
                    placeholder="PDF'den ayıklanan metin..."
                  />
                )}
              </div>
            )}
          </div>

          {/* ── Output Panel ── */}
          <div className="panel relative">
            <div className="panel-header">
              <span className="panel-title green-icon">
                <CheckCircle size={18} />
                Basitleştirilmiş Sonuç
              </span>
              {/* Output Toolbar */}
              {isOutputReady && (
                <div className="output-toolbar">
                  <button onClick={handleCopy} className="toolbar-btn" title="Metni Kopyala">
                    <Copy size={14} /> Kopyala
                  </button>
                  <button onClick={handleDownloadPdf} className="toolbar-btn toolbar-btn--accent" title="PDF İndir">
                    <Download size={14} /> PDF
                  </button>
                </div>
              )}
            </div>

            <div className="relative flex-grow">
              <textarea
                readOnly
                className="panel-textarea output"
                value={displayedText}
                placeholder=""
              />

              {displayedText && displayedText.length < outputText.length && (
                <span className="typewriter-cursor"></span>
              )}

              {isLoading && (
                <div className="skeleton-loader"></div>
              )}

              {!displayedText && !isLoading && (
                <div className="watermark">
                  <span>Sonuç Bekleniyor...</span>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Action Area */}
        <div className="action-wrapper">
          <button
            onClick={handleSimplify}
            disabled={isLoading || !inputText.trim()}
            className="btn-action"
          >
            {isLoading ? (
              <>
                <Activity className="animate-spin" size={24} />
                Yapay Zeka İşliyor...
              </>
            ) : (
              'Metni Basitleştir'
            )}
          </button>
        </div>
      </div>
    </main>
  );
});

export default SimplifierTool;
