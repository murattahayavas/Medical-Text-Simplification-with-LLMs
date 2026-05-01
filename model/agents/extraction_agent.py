from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
import json

class ExtractionAgent:
    """
    2. Adım: Ön İşleme ve Ekstraksiyon Ajanı.
    Rapordaki teknik terimleri ve ICD-10 kodlarını ayıklar.
    """
    def __init__(self, groq_api_key: str):
        self.llm = ChatGroq(
            model_name="llama-3.3-70b-versatile",
            temperature=0, # Analiz için 0 (net sonuç)
            groq_api_key=groq_api_key
        )

        # agents/extraction_agent.py içindeki ilgili kısım:

    def extract_info(self, report_text: str):
        print("[INFO] Rapor analiz ediliyor, veriler ayıklanıyor...")
        prompt = ChatPromptTemplate.from_messages([
            ("system", (
                "Sen bir tıbbi veri analiz uzmanısın. Sana verilen rapordan şunları ayıkla:\n"
                "1. ICD-10 Kodları (Varsa)\n"
                "2. Sadeleştirilmesi gereken en önemli 3-5 teknik terim.\n"
                "Yanıtı sadece şu JSON formatında ver:\n"
                "{{ \"icd_codes\": \"...\", \"complex_terms\": \"...\" }}" # ÇİFT PARANTEZ KULLANDIK
            )),
            ("user", "{report_text}")
        ])
        
        chain = prompt | self.llm
        # Artık sadece report_text bekleyecek, hata vermeyecek.
        response = chain.invoke({"report_text": report_text})
        

    
        
        
        # JSON parse işlemi (Basitleştirilmiş)
        try:
            return json.loads(response.content.replace("'", '"'))
        except:
            # Fallback: Eğer model JSON formatında hata yaparsa
            return {"icd_codes": "Tespit edilemedi", "complex_terms": "Teknik jargon"}