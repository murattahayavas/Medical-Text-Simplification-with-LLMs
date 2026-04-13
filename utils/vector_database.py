import faiss
from sentence_transformers import SentenceTransformer
import numpy as np
import os

class MedicalVectorStore:
    def __init__(self, data_path, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.data_path = data_path
        self.index = None
        self.source_sentences = []
        self.target_sentences = []

    def load_and_build(self):
        """Train verilerini yükler ve FAISS indeksini oluşturur."""
        src_path = os.path.join(self.data_path, "train.source")
        tgt_path = os.path.join(self.data_path, "train.target")

        print(f"[INFO] Veriler yükleniyor: {src_path}")
        with open(src_path, 'r', encoding='utf-8') as f:
            self.source_sentences = [line.strip() for line in f.readlines()]
        with open(tgt_path, 'r', encoding='utf-8') as f:
            self.target_sentences = [line.strip() for line in f.readlines()]

        print(f"[INFO] {len(self.source_sentences)} satır vektörleştiriliyor...")
        # Cümleleri sayılara (embedding) çevir
        embeddings = self.model.encode(self.source_sentences, show_progress_bar=True)
        
        # FAISS Indeksi oluştur (L2 mesafesi ile en yakın benzeri bulur)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(np.array(embeddings).astype('float32'))
        print("[INFO] FAISS İndeksi başarıyla oluşturuldu.")

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