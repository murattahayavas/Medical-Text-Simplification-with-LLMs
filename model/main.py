from agents.groq_generation_agent import GenerationAgent
from agents.extraction_agent import ExtractionAgent
from utils.vector_database import MedicalVectorStore
import os
import re
from pathlib import Path
from utils.metrics import (
    değerlendir_ve_seç, 
    atesman_skoru_hesapla, 
    bertscore_hesapla, 
    sari_hesapla, 
    metrik_grafik_ciz,
    metrik_rehberi_yazdir # Yeni eklediğimiz rehber
)

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "data-1024"

def get_groq_api_key():
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        return api_key.strip()

    key_file = BASE_DIR / "utils" / "api_keys.txt"
    if key_file.exists():
        key_text = key_file.read_text(encoding="utf-8")
        match = re.search(r"gsk_[A-Za-z0-9_-]+", key_text)
        if match:
            return match.group(0)

    raise RuntimeError("GROQ_API_KEY bulunamadi. Ortam degiskeni olarak ekleyin veya Model/utils/api_keys.txt dosyasina yazin.")

def klinik_metin_isleme_sistemi(rapor):
    API_KEY = get_groq_api_key()
    
# 1. Başlangıç ve Metrik Rehberi
    metrik_rehberi_yazdir()
    
    # 2. Ajanları ve Veri Deposunu Başlat
    extractor = ExtractionAgent(groq_api_key=API_KEY)
    agent = GenerationAgent(groq_api_key=API_KEY)
    v_store = MedicalVectorStore(str(DATA_PATH))
    v_store.load_or_build()

    # ADIM 2: EXTRACTION (Bilgi Ayıklama)
    extracted_data = extractor.extract_info(rapor)
    icd = extracted_data.get('icd_codes', "")
    terimler = extracted_data.get('complex_terms', "")
    print(f"\n[INFO] Ayıklanan ICD Kodları: {icd}")
    print(f"[INFO] Odaklanılacak Terimler: {terimler}")

    # ADIM 3: RAG (Dinamik Örnek Getirme)
    print("\n[RAG] Veri setinden en benzer vaka örnekleri getiriliyor...")
    dinamik_ornekler = v_store.get_similar_examples(rapor, n=3)
    
    # Dinamik Referans: SARI metriği için RAG'den gelen en yakın örneğin hedefini kullanıyoruz
    dynamic_reference = dinamik_ornekler[0]['output'] if dinamik_ornekler else ""

    # ADIM 4: GENERATION (Taslak Üretimi)
    print("\n" + "="*40)
    print("🚀 TASLAK ÜRETİMİ VE ÇOK BOYUTLU PUANLAMA")
    print("="*40)

    taslaklar = agent.generate_drafts(rapor, icd, dinamik_ornekler)
    atesman_skorlari = []
    bert_skorlari = []
    sari_skorlari = []

    for i, t in enumerate(taslaklar):
        # Skorları hesapla
        puan = atesman_skoru_hesapla(t)
        bert = bertscore_hesapla(rapor, t)
        sari = sari_hesapla(
            source=rapor, 
            prediction=t, 
            reference=dynamic_reference 
        )
        atesman_skorlari.append(puan)
        bert_skorlari.append(bert)
        sari_skorlari.append(sari)

        print(f"\n--- TASLAK {i+1} ---")
        print(f"📈 Ateşman: {puan:.2f} (Okunabilirlik)")
        print(f"🧠 BERTScore: {bert:.2f} (Anlamsal Sadakat)")
        print(f"✨ SARI: {sari:.2f} (Sadeleştirme Kalitesi)")
        print(f"📝 Metin: {t[:150]}...") # İlk 150 karakter
        print("-" * 30)

    # Metrikleri görselleştir
    metrik_grafik_ciz(atesman_skorlari, bert_skorlari, sari_skorlari,model_ismini=agent.model_name)
    # ADIM 5: EVALUATION & DECISION (Karar Verme)
    # Karar mekanizması artık BERTScore'u da dikkate alıyor (metrics.py güncellemenle uyumlu)
    en_iyi_metin, skor = değerlendir_ve_seç(taslaklar, icd, orijinal_rapor=rapor, reference=dynamic_reference)
    print(f"\n[KARAR] Seçilen En İyi Taslağın Genel Başarı Skoru: {skor:.2f}")

    # ADIM 6: REFLEXION (Öz-Yansıma Döngüsü)
    if skor < 0.75: # Eşik değerini biraz daha profesyonel seviyeye çektik
        print(f"\n[UYARI] Hedef skorun altında kalındı. Reflexion iyileştirmesi başlatılıyor...")
        feedback = (
        "Metni yeniden yaz ama şu kurallara kesinlikle uy:\n"
        "1. Tıbbi terimleri basit Türkçeye çevir (örn: 'postoperatif' → 'ameliyat sonrası').\n"
        "2. Uzun cümleleri kısa ve net cümlelere böl.\n"
        "3. Gereksiz detayları ve teknik ifadeleri çıkar.\n"
        "4. Metin 12 yaşındaki birinin anlayacağı kadar basit olmalı.\n"
        "5. Anlamı koru ama dili sadeleştir.\n"
    )

        final_metin = agent.refine_draft(rapor, en_iyi_metin, feedback, icd)

        # İyileştirilmiş metnin metriklerini son kez ölç
        yeni_atesman = atesman_skoru_hesapla(final_metin)
        yeni_bert = bertscore_hesapla(rapor, final_metin)
        yeni_sari = sari_hesapla(rapor, final_metin, dynamic_reference)
        # REFLEXION sonrası METRİK KORUMA (ÇOK ÖNEMLİ)

        if yeni_bert < 0.55:
            print("[REFLEXION-REJECT] Anlam bozuldu → eski metin kullanılıyor")
            return en_iyi_metin

        if yeni_atesman < 30:
            print("[REFLEXION-REJECT] Okunabilirlik düştü → eski metin kullanılıyor")
            return en_iyi_metin

        if yeni_sari < sari_skorlari[0] * 0.9:
            print("[REFLEXION-REJECT] Sadeleştirme kötü → eski metin kullanılıyor")
            return en_iyi_metin
        

        print(f"\n" + "✅"*10 + " REFLEXION SONUÇLARI " + "✅"*10)
        print(f"Yeni Ateşman: {yeni_atesman:.2f} | Yeni BERTScore: {yeni_bert:.2f} | Yeni SARI: {yeni_sari:.2f}")
        return final_metin

    return en_iyi_metin

if __name__ == "__main__":
    sample_report = """

Bulgular

Hastanın BOYUN USG tetkikinde; Her iki tarafta parotis gland boyutları tabiidir. Parotis glandlarında eko yapısı homojen karakterde olup yer işgal eden kitlesel lezyon, kalkül veya duktalektazi saptanmamıştır. Submandibular glandlar normal boyut ve eko yapısındadırlar. Tiroidektomi öykülü hastada sağ lob ve isthmusta nüks-rezidü lehine bulgu saptanmadı. Sol tiroid lojunda (APXMLXCC) 14x7x16 mm boyutunda hipoekoik görünüm izlendi (nüks?, rezidü?). Klinik gereklilik halinde sintigrafi ile birlikte değerlendirilmesi önerilir. Boyunda patolojik boyutlarda lenf nodülü saptanmamıştır.

Sonuç ve Öneriler

Hastanın BOYUN USG tetkikinde; Her iki tarafta parotis gland boyutları tabiidir. Parotis glandlarında eko yapısı homojen karakterde olup yer işgal eden kitlesel lezyon, kalkül veya duktalektazi saptanmamıştır. Submandibular glandlar normal boyut ve eko yapısındadırlar. Tiroidektomi öykülü hastada sağ lob ve isthmusta nüks-rezidü lehine bulgu saptanmadı. Sol tiroid lojunda (ADVMLVCC) 14~7~16 mm boyutunda
    """

    final_sonuc = klinik_metin_isleme_sistemi(sample_report)
    print("\n[FINAL DEBUG]")
    print("Ateşman:", atesman_skoru_hesapla(final_sonuc))
    print("BERT:", bertscore_hesapla(sample_report, final_sonuc))
    print("SARI:", sari_hesapla(sample_report, final_sonuc, dynamic_reference if 'dynamic_reference' in locals() else final_sonuc))

    print("\n" + "█"*60)
    print("HASTAYA VERİLECEK FİNAL METİN (ONAYLANDI):")
    print(final_sonuc)
    print("█"*60)
