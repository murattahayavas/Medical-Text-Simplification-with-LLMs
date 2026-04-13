import os
from typing import List
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate
from langchain.schema import SystemMessage

class GenerationAgent:
    """
    Doktor Dili -> Hasta Dili projesi için 3. Adım: Taslak Üretim Ajanı.
    Bu ajan, teknik klinik raporları alır ve n=5 adet sadeleştirilmiş taslak üretir.
    """

    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        # Model ayarları (n=5 taslak ve yaratıcılık için temperature 0.7)
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=0.7,
            n=5,
            openai_api_key=api_key
        )
        self.prompt = self._build_prompt_template()

    def _build_prompt_template(self) -> ChatPromptTemplate:
        """
        GitHub reposundan (Cochrane) esinlenilen Few-Shot örneklerini 
        ve sistem kurallarını içeren prompt yapısını kurar.
        """
        
        # 1. GitHub reposundan seçilen 'Altın Standart' örnekler (Few-Shot)
        # Buradaki örnekler modelin 'stilini' belirler.
        examples = [
            {
                "input": "Patient presents with acute myocardial infarction with ST-elevation.",
                "output": "Hasta, kalp kasını besleyen damarların tıkanması sonucu oluşan 'kalp krizi' tablosu ile gelmiştir."
            },
            {
                "input": "Computed tomography revealed a hyperdense lesion in the left hemisphere.",
                "output": "Bilgisayarlı tomografi taramasında beynin sol tarafında kanama veya kitle şüphesi uyandıran yoğun bir alan saptanmıştır."
            }
        ]

        # 2. Örneklerin formatlanması
        example_prompt = ChatPromptTemplate.from_messages([
            ("user", "{input}"),
            ("ai", "{output}"),
        ])

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=examples,
        )

        # 3. Ana Sistem Talimatları (İpek'in makalesindeki doğruluk kriterleri dahil)
        return ChatPromptTemplate.from_messages([
            ("system", (
                "Sen profesyonel bir tıbbi iletişim asistanısın.\n"
                "GÖREVİN: Teknik klinik raporları, tıbbi doğruluğu %100 koruyarak "
                "10. sınıf seviyesindeki bir hastanın anlayacağı sade bir dile çevirmektir.\n\n"
                "KURALLAR:\n"
                "- Bilgiyi asla uydurma (Hallucination yapma).\n"
                "- Cümleleri kısa ve öz tut.\n"
                "- Teknik terimleri mutlaka parantez içinde basitçe açıkla.\n"
                "- Rapordaki ICD-10 kodlarını ({icd_codes}) metnin içine doğal bir şekilde yerleştir."
            )),
            few_shot_prompt,
            ("user", "Lütfen şu raporu sadeleştir: {report_text}")
        ])

    def generate_drafts(self, report_text: str, icd_codes: str) -> List[str]:
        """
        Verilen teknik metinden 5 adet farklı taslak mektup üretir.
        """
        print(f"[INFO] Taslak üretimi başlatıldı... (ICD Kodları: {icd_codes})")
        
        # Zinciri oluştur ve çalıştır
        chain = self.prompt | self.llm
        response = chain.generate([self.prompt.format_messages(
            report_text=report_text, 
            icd_codes=icd_codes
        )])

        # 5 farklı taslağı liste olarak döndür
        drafts = [gen[0].text for gen in response.generations]
        return drafts

# --- KULLANIM ÖRNEĞİ (Test) ---
if __name__ == "__main__":
    # API anahtarını buraya ekle veya çevre değişkeninden al
    MY_API_KEY = "your-api-key-here"
    
    # Ajanı başlat
    agent = GenerationAgent(api_key=MY_API_KEY)
    
    # 2. Adımdan (Preprocessing) geldiği varsayılan veriler
    sample_report = "74-year-old male with a history of hypertension. Echocardiogram shows left ventricular hypertrophy."
    sample_icd = "I10 (Hipertansiyon), I51.7 (Kardiyomegali)"

    # Taslakları üret
    mevcut_taslaklar = agent.generate_drafts(sample_report, sample_icd)

    # Sonuçları ekrana bas
    for idx, text in enumerate(mevcut_taslaklar):
        print(f"\n--- TASLAK {idx+1} ---")
        print(text)