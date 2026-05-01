import os
from typing import List
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

class GenerationAgent:
    def __init__(self, groq_api_key: str, model_name: str = "meta-llama/llama-4-scout-17b-16e-instruct"):
        self.model_name = model_name
        self.llm = ChatGroq(
            model_name=model_name,
            temperature=0.7,
            groq_api_key=groq_api_key
            #model_kwargs={"reasoning_format": None}
        )
        
        
    def _build_dynamic_prompt(self, dynamic_examples: List[dict], icd_codes: str) -> ChatPromptTemplate:
        """FAISS'ten gelen dinamik örneklerle promptu her seferinde yeniden kurar."""
        example_prompt = ChatPromptTemplate.from_messages([
            ("user", "{input}"),
            ("ai", "{output}"),
        ])

        few_shot_prompt = FewShotChatMessagePromptTemplate(
            example_prompt=example_prompt,
            examples=dynamic_examples, # FAISS'ten gelen liste buraya girer
        )

        return ChatPromptTemplate.from_messages([
            ("system", (
                "Sen tıbbi bir editörsün. Klinik raporları 10. sınıf seviyesinde sadeleştir.\n"
                "KESİN KURALLAR:\n"
                "1. %100 TÜRKÇE: Asla İngilizce kelime kullanma (Örn: 'slightly' yerine 'hafifçe' yaz).\n"
                "2.  Her bir ICD kodunu {icd_codes}, ilgili olduğu cümlenin hemen yanına parantez içinde ekle. Asla metnin sonuna toplu halde yazma.\n"
                "3. KISA TUT: Gereksiz teknik detayları at, sadece hasta için kritik olanı sadeleştir.\n"
                "4. DOĞRULUK: Bilgiyi değiştirme."
            )),
            few_shot_prompt,
            ("user", "Lütfen şu raporu sadeleştir: {report_text}")
        ])

    def generate_drafts(self, report_text: str, icd_codes: str, dynamic_examples: List[dict]) -> List[str]:
        """Dinamik örnekleri kullanarak istenen taslakları üretir."""
        print(f"[INFO] Taslak üretimi başlatıldı... (Dinamik RAG örnekleri kullanılıyor)")
        
        # Her rapor için gelen özel örneklerle promptu oluştur
        prompt = self._build_dynamic_prompt(dynamic_examples, icd_codes)
        chain = prompt | self.llm
        
        drafts = []
        for i in range(3):
            response = chain.invoke({
                "report_text": report_text,
                "icd_codes": icd_codes
            })
            drafts.append(response.content)
            print(f"Taslak {i+1} üretildi.")
            
        return drafts

   



    def refine_draft(self, report_text: str, draft: str, feedback: str, icd_codes: str) -> str:
        """
        5. Adım: Öz-Yansıma (Reflexion) İyileştirme Metodu.
        Geri bildirime göre metni tekrar düzenler.
        """
        print("[REFLEXION] Metin iyileştiriliyor...")
        refine_prompt = ChatPromptTemplate.from_messages([
            ("system", "Sen bir editörsün. Aşağıdaki taslak tıbbi raporu, verilen geri bildirimleri dikkate alarak daha sade ve anlaşılır hale getir."),
            ("user", (
                "Orijinal Rapor: {report_text}\n"
                "Mevcut Taslak: {draft}\n"
                "Geri Bildirim: {feedback}\n"
                "Kural: ICD Kodlarını ({icd_codes}) koru ve metni 10. sınıf seviyesine çek."
            ))
        ])
        
        chain = refine_prompt | self.llm
        response = chain.invoke({
            "report_text": report_text,
            "draft": draft,
            "feedback": feedback,
            "icd_codes": icd_codes
        })
        return response.content