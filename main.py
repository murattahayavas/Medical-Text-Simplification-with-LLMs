from agents.groq_generation_agent import GenerationAgent
from agents.extraction_agent import ExtractionAgent
from utils.metrics import değerlendir_ve_seç, atesman_skoru_hesapla
from utils.vector_database import MedicalVectorStore # İkisini de import et
import os
from pathlib import Path
from dotenv import load_dotenv

def klinik_metin_isleme_sistemi(rapor):
    base_dir = Path(__file__).resolve().parent
    load_dotenv(base_dir / ".env")
    data_path = base_dir / "data" / "data-1024"
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY ortam değişkeni tanımlı değil.")
    
    # 1. Ajanları Başlat
    extractor = ExtractionAgent(groq_api_key=api_key)
    agent = GenerationAgent(groq_api_key=api_key)
    v_store = MedicalVectorStore(str(data_path))
    v_store.load_and_build()
    
    # ADIM 2: EXTRACTION
    extracted_data = extractor.extract_info(rapor)
    icd = extracted_data.get('icd_codes', "")
    terimler = extracted_data.get('complex_terms', "")
    print(f"[INFO] Ayıklanan ICD Kodları: {icd}")

    # ADIM 3: RAG (Dinamik Örnek Getirme)
    print("\n[RAG] Benzer vakalar veri setinden getiriliyor...")
    dinamik_ornekler = v_store.get_similar_examples(rapor, n=3)

    # ADIM 4: GENERATION 
    print("\n" + "="*30)
    print("TASLAK ÜRETİMİ VE PUANLAMA")
    print("="*30)
    
    taslaklar = agent.generate_drafts(rapor, icd, dinamik_ornekler)   

    #Her taslağı ve puanını anlık yazdır
    for i, t in enumerate(taslaklar):
        puan = atesman_skoru_hesapla(t)
        print(f"\n--- TASLAK {i+1} ---")
        print(f"Ateşman Skoru: {puan:.2f}")
        print(f"Metin: {t}")
        print("-" * 20)

    #ADIM 5: EVALUATION & DECISION
    en_iyi_metin, skor = değerlendir_ve_seç(taslaklar, icd)
    print(f"\n[KARAR] Seçilen En İyi Taslağın Başarı Skoru: {skor:.2f}")
    
    #ADIM 6: REFLEXION
    if skor < 0.70:
        print(f"[UYARI] Düşük Skor ({skor:.2f}). Reflexion başlatılıyor...")
        feedback = f"Metin teknik kalmış veya ICD kodlarını içermiyor. Şunlara odaklan: {terimler}. Daha sade yaz."
        
        final_metin = agent.refine_draft(rapor, en_iyi_metin, feedback, icd)
        
        # İyileştirilmiş metni tekrar değerlendir
        _, yeni_skor = değerlendir_ve_seç([final_metin], icd)
        yeni_atesman = atesman_skoru_hesapla(final_metin)
        
        print(f"\n[REFLEXION TAMAMLANDI]")
        print(f"Yeni Başarı Skoru: {yeni_skor:.2f} | Yeni Ateşman: {yeni_atesman:.2f}")
        return final_metin
    
    return en_iyi_metin

if __name__ == "__main__":
    # Çok satırlı metinler için mutlaka üç tırnak kullanıyoruz:
    sample_report = """
    

    Bulgular:
    TEKNİK: Üriner sistemde taş araştırılan olguda İV kontrastsız BT: Bu rapor iki tetkike aittir.
    Sağ böbrek lokalizasyonu, parankim kalınlığı, konturları normaldir.
    Sağ üreterde belirgin genişleme yoktur. Üreter trasesinde opak kalkül görülmemiştir.
    Sağ böbrek alt polde 6 mm ve 4 mm çaplarında hiperdens kalkül imajları ile birlikte grade 1 pelvikaliektazik değişiklik izlenmiştir.
    Sağ böbrek boyutlarında hipertrofi kompansatuar değişiklikler mevcuttur.
    Sol böbrek normal lokalizasyonunda izlenmemiştir. (Sol böbrek nefrektomize)
    Sol renal fossada nüks ve rezidüye ait patolojik dansite oluşum izlenmemiştir.
    Mesane duvar kalınlığı normaldir. Mesane içerisinde opak taş görülmemiştir.
    Pelvik yağlı planlar açıktır. İntrapelvik ya da inguinal lenfadenopati görülmedi.
    İnceleme planına giren sürrenal glandlar, pankreas, paraaortik alan normaldir.
    Batın duvarı oluşumları normaldir. Batın içerisinde serbest sıvı görülmedi.

    Sonuç ve Öneriler:
    Sağ böbrek alt polde hiperdens kalkül imajları, grade 1 pelvikaliektazi
    Sağ böbrek boyutlarında hipertrofi kompansatuar değişiklikler
    Sol böbrek nefrektomize
    """

    # Sistemi çalıştır
    final_sonuc = klinik_metin_isleme_sistemi(sample_report)
    
    print("\n" + "="*50)
    print("HASTAYA VERİLECEK FİNAL METİN (REFLEXION ONAYLI):")
    print(final_sonuc)
    print("="*50)