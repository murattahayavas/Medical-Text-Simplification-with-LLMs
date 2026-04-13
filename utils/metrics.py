import re

def atesman_skoru_hesapla(metin):
    unlu_harfler = "aeıioöuüAEIİOÖUÜ"
    cumleler = re.split(r'[.!?]+', metin.strip())
    cumle_sayisi = len([c for c in cumleler if c.strip()])
    kelimeler = metin.split()
    kelime_sayisi = len(kelimeler)
    hece_sayisi = sum(1 for harf in metin if harf in unlu_harfler)
    
    if kelime_sayisi == 0 or cumle_sayisi == 0: return 0
    
    return 198.825 - (40.175 * (hece_sayisi / kelime_sayisi)) - (2.610 * (kelime_sayisi / cumle_sayisi))

def değerlendir_ve_seç(taslaklar, orijinal_icd):
    en_iyi_skor = -1
    en_iyi_metin = ""
    
    # Regex ile kodları temizle (Örn: "I10, I51.7" -> ["I10", "I51.7"])
    temiz_kodlar = re.findall(r'[A-Z][0-9][0-9A-Z\.]+', orijinal_icd)

    for taslak in taslaklar:
        # 1. Okunabilirlik Puanı (%20)
        okunabilirlik = atesman_skoru_hesapla(taslak) / 100
        
        # 2. Doğruluk Puanı (%80)
        if temiz_kodlar:
            # Sadece temizlenmiş kod listesi üzerinden sayım yapıyoruz
            gecen_kodlar = sum(1 for kod in temiz_kodlar if kod in taslak)
            dogruluk = gecen_kodlar / len(temiz_kodlar)
        else:
            dogruluk = 1 # Kod yoksa hata da yoktur
        
        # Toplam Skor Hesaplama
        toplam_puan = (okunabilirlik * 0.2) + (dogruluk * 0.8)
        
        if toplam_puan > en_iyi_skor:
            en_iyi_skor = toplam_puan
            en_iyi_metin = taslak
            
    return en_iyi_metin, en_iyi_skor

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






