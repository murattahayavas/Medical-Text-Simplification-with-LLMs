from datetime import datetime
import os 
import matplotlib.pyplot as plt
from bert_score import score
import re
import numpy as np

def metrik_rehberi_yazdir():
    """Metriklerin ne anlama geldiğini kullanıcıya açıklar."""
    rehber = {
        "Ateşman": "Metnin okunabilirlik seviyesi. 70+ skorlar halkın anlayabileceği sadeliktedir.",
        "BERTScore": "Anlamsal Sadakat. Orijinal raporun anlamı ne kadar korundu? (Hedef > 0.60)",
        "SARI": "Sadeleştirme Başarısı. Gereksiz kelimeler silinmiş mi, açıklayıcı kelimeler eklenmiş mi?",
    }
    print("\n" + "="*50 + "\n📊 METRİK REHBERİ")
    for isim, aciklama in rehber.items():
        print(f"🔹 {isim}: {aciklama}")
    print("="*50 + "\n")

def atesman_skoru_hesapla(metin):
    unlu_harfler = "aeıioöuüAEIİOÖUÜ"
    metin_temiz = re.sub(r'[^\w\s]', '', metin.lower()) # Noktalama temizliği
    cumleler = re.split(r'[.!?]+', metin.strip())
    cumle_sayisi = len([c for c in cumleler if c.strip()])
    kelimeler = metin_temiz.split()
    kelime_sayisi = len(kelimeler)
    hece_sayisi = sum(1 for harf in metin if harf in unlu_harfler)

    if kelime_sayisi == 0 or cumle_sayisi == 0: return 0
    return 198.825 - (40.175 * (hece_sayisi / kelime_sayisi)) - (2.610 * (kelime_sayisi / cumle_sayisi))

def bertscore_hesapla(referans, aday):
    # lang="tr" kullanarak Türkçe BERT modelini (dbmdz) çağırır
    P, R, F1 = score([aday], [referans], lang="tr", verbose=False)
    return float(F1.mean())

def sari_hesapla(source, prediction, reference):
    # Küçük harf normalizasyonu eklenmiş hali
    def tokenize(text): return set(re.sub(r'[^\w\s]', '', text.lower()).split())
    
    s_tokens, p_tokens, r_tokens = tokenize(source), tokenize(prediction), tokenize(reference)

    keep = len((s_tokens & p_tokens) & r_tokens)
    add = len((p_tokens - s_tokens) & r_tokens)
    delete = len((s_tokens - p_tokens) - r_tokens)

    keep_score = keep / len(r_tokens) if r_tokens else 0
    add_score = add / len(r_tokens) if r_tokens else 0
    delete_score = delete / len(s_tokens) if s_tokens else 0

    return (keep_score + add_score + delete_score) / 3

def değerlendir_ve_seç(taslaklar, orijinal_icd, orijinal_rapor, reference):
    en_iyi_skor = -1
    en_iyi_metin = ""
    temiz_kodlar = re.findall(r'[A-Z][0-9][0-9A-Z\.]+', orijinal_icd)

    for taslak in taslaklar:
        okunabilirlik = atesman_skoru_hesapla(taslak) / 100
        bert = bertscore_hesapla(orijinal_rapor, taslak)
        sari = sari_hesapla(orijinal_rapor, taslak, reference)
        # HARD FILTER (anlam çok bozuksa direkt at)
        if bert < 0.55:
            continue

        # Okunabilirliği clamp et (aşırı dominance'ı engelle)
        okunabilirlik = min(okunabilirlik, 0.85)
        
        
        if temiz_kodlar:
            gecen_kodlar = sum(1 for kod in temiz_kodlar if kod in taslak)
            dogruluk = gecen_kodlar / len(temiz_kodlar)
        else:
            dogruluk = 1

        toplam_puan = (
        0.35 * bert +
        0.25 * dogruluk +
        0.2 * okunabilirlik +
        0.2 * sari
    )
        # SARI düşükse ceza ver
        if sari < 0.2:
            continue

        print(f"[DEBUG] bert={bert:.2f}, sari={sari:.2f}, ok={okunabilirlik:.2f}, icd={dogruluk:.2f}, total={toplam_puan:.2f}")
        if toplam_puan > en_iyi_skor:
            en_iyi_skor = toplam_puan
            en_iyi_metin = taslak

    return en_iyi_metin, en_iyi_skor



def metrik_grafik_ciz(atesman_skorlari, bert_skorlari, sari_skorlari, model_ismini="Bilinmiyor"):
    """Tüm metrikleri analiz eder ve gelişmiş görselleştirmeler sunar."""
    os.makedirs("plots", exist_ok=True)
    zaman = datetime.now().strftime("%Y%m%d_%H%M%S")
    # metrics.py içindeki model_tag satırını bununla değiştir:
    model_tag = model_ismini.replace("/", "_").replace("\\", "_").replace("-", "_").replace(".", "_").replace(":", "_")

    # 1. ÇİZGİ GRAFİK (Geleneksel İzleme)
    plt.figure(figsize=(10, 6))
    x = list(range(1, len(bert_skorlari) + 1))
    atesman_norm = [s / 100 for s in atesman_skorlari]
    
    plt.plot(x, atesman_norm, marker='s', label="Ateşman (Normalize)")
    plt.plot(x, bert_skorlari, marker='o', label="BERTScore")
    plt.plot(x, sari_skorlari, marker='^', label="SARI")
    
    plt.title(f"Performans Analizi - {model_ismini}")
    plt.xlabel("Taslak No")
    plt.ylabel("Skor (0-1)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig(f"plots/line_{model_tag}_{zaman}.png")
    plt.close()

    # 2. RADAR GRAFİĞİ (En İyi Taslağın Karakteri)
    # En yüksek BERTScore alan taslağı örnek alalım
    en_iyi_idx = np.argmax(bert_skorlari)
    labels = ['Okunabilirlik', 'Anlamsal Sadakat', 'Sadeleştirme Başarısı']
    stats = [atesman_norm[en_iyi_idx], bert_skorlari[en_iyi_idx], sari_skorlari[en_iyi_idx]]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    stats = stats + stats[:1]
    angles = angles + angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, stats, color='blue', alpha=0.25)
    ax.plot(angles, stats, color='blue', linewidth=2)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    plt.title(f"Taslak {en_iyi_idx+1} Profili")
    plt.savefig(f"plots/radar_{model_tag}_{zaman}.png")
    plt.close()

    # 3. SCATTER PLOT (Doğruluk vs Sadelik Dengesi)
    plt.figure(figsize=(8, 6))
    plt.scatter(atesman_norm, bert_skorlari, s=100, c='red', alpha=0.6)
    for i, txt in enumerate(x):
        plt.annotate(f"T{txt}", (atesman_norm[i], bert_skorlari[i]))
    
    plt.xlabel("Okunabilirlik (Ateşman)")
    plt.ylabel("Anlamsal Sadakat (BERTScore)")
    plt.title("Doğruluk ve Sadelik Dengesi")
    plt.grid(True, linestyle='--')
    plt.savefig(f"plots/scatter_{model_tag}_{zaman}.png")
    plt.close()

    print(f"[INFO] 3 farklı grafik başarıyla 'plots/' klasörüne kaydedildi.")
"""
    Türkçe metinler için Ateşman Okunabilirlik İndeksi'ni hesaplar.
    Formül: 198.825 - 40.175 * (Toplam Hece / Toplam Kelime) - 2.610 * (Toplam Kelime / Toplam Cümle)
    
    Skor Aralıkları:
    90-100: Çok Kolay (4. Sınıf altı)
    70-89:  Kolay (5-6. Sınıf)
    50-69:  Orta Güçlükte (7-8. Sınıf)
    30-49:  Zor (9-12. Sınıf / Lise)
    1-29:   Çok Zor (Üniversite ve üstü)
"""






