import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import pickle  

class MedicalVectorStore:
    def __init__(self, data_path, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.data_path = data_path
        # Kayıt dosyalarının yolları
        self.index_path = os.path.join(data_path, "medical_index.faiss")
        self.data_path_pkl = os.path.join(data_path, "sentences_data.pkl")
        
        self.index = None
        self.source_sentences = []
        self.target_sentences = []

    def load_or_build(self):
        """Eğer hazır indeks varsa yükler, yoksa baştan oluşturup kaydeder."""
        
        # 1. Kontrol: Dosyalar daha önce oluşturulmuş mu?
        if os.path.exists(self.index_path) and os.path.exists(self.data_path_pkl):
            print(f"[INFO] Hazır indeks ve veri seti bulundu. Yükleniyor...")
            
            # FAISS indeksini yükle
            self.index = faiss.read_index(self.index_path)
            
            # Cümleleri (Source/Target) yükle
            with open(self.data_path_pkl, 'rb') as f:
                data = pickle.load(f)
                self.source_sentences = data['source']
                self.target_sentences = data['target']
            
            print(f"[SUCCESS] {len(self.source_sentences)} vaka 1 saniyede yüklendi.")
            
        else:
            # 2. Dosyalar yoksa: Baştan vektörleştir
            print(f"[INFO] İndeks bulunamadı. Vektörleştirme başlatılıyor (bu işlem zaman alabilir)...")
            
            src_path = os.path.join(self.data_path, "train.source")
            tgt_path = os.path.join(self.data_path, "train.target")

            with open(src_path, 'r', encoding='utf-8') as f:
                self.source_sentences = [line.strip() for line in f.readlines()]
            with open(tgt_path, 'r', encoding='utf-8') as f:
                self.target_sentences = [line.strip() for line in f.readlines()]

            # Vektörleştirme
            embeddings = self.model.encode(self.source_sentences, show_progress_bar=True)
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            self.index.add(np.array(embeddings).astype('float32'))

            # 3. Kaydet: Bir sonraki sefer bekleme
            print(f"[INFO] Oluşturulan indeks diske kaydediliyor...")
            faiss.write_index(self.index, self.index_path)
            with open(self.data_path_pkl, 'wb') as f:
                pickle.dump({
                    'source': self.source_sentences,
                    'target': self.target_sentences
                }, f)
            print("[SUCCESS] FAISS İndeksi ve cümleler başarıyla kaydedildi.")

    def get_similar_examples(self, query_text, n=3):
        """Yeni gelen rapora en benzer n adet 'teknik-sade' çiftini bulur."""
        query_embedding = self.model.encode([query_text])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), n)
        
        examples = []
        for idx in indices[0]:
            examples.append({
                "input": self.source_sentences[idx],
                "output": self.target_sentences[idx]
            })
        return examples