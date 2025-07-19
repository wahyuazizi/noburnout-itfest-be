from openai import AsyncAzureOpenAI
from typing import Optional
import logging
from app.config import settings

logger = logging.getLogger(__name__)

class AzureOpenAIService:
    """Service for interacting with Azure OpenAI."""
    
    def __init__(self):
        self.client = AsyncAzureOpenAI(
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint
        )
        self.deployment_name = settings.azure_openai_deployment_name
    
    async def create_presentation_content(self, document_text: str, max_tokens: int = 2000) -> str:
        """
        Create presentation content from document text.
        
        Args:
            document_text: The full text from the document.
            max_tokens: Maximum tokens for the generated content.
            
        Returns:
            A JSON string representing the presentation structure.
        """
        try:
            system_prompt = """Anda adalah asisten ahli yang bertugas membuat konten presentasi dari sebuah dokumen.
            Berdasarkan teks yang diberikan, buatlah struktur presentasi yang terdiri dari judul dan serangkaian slide.
            Setiap slide harus memiliki judul dan konten. Konten dapat berupa poin-poin (bullet points) atau paragraf singkat yang ringkas.
            
            Format output harus berupa JSON yang valid, seperti contoh ini:
            {
              "title": "Judul Presentasi",
              "slides": [
                {
                  "title": "Judul Slide 1",
                  "content": [
                    "Ini adalah contoh konten dalam bentuk paragraf singkat, merangkum ide utama dari bagian ini.",
                    "Paragraf bisa digunakan untuk penjelasan yang lebih naratif."
                  ]
                },
                {
                  "title": "Judul Slide 2",
                  "content": [
                    "Poin penting pertama dalam bentuk bullet point.",
                    "Poin penting kedua untuk menyoroti detail spesifik."
                  ]
                }
              ]
            }
            
            Pastikan konten tetap ringkas, informatif, dan relevan dengan dokumen sumber. Gunakan Bahasa Indonesia."""
            
            user_prompt = f"""Buatkan konten presentasi dari dokumen berikut:

{document_text}"""
            
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.5,
                response_format={"type": "json_object"}
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error creating presentation content: {str(e)}")
            raise Exception(f"Failed to create presentation content: {str(e)}")

# Create service instance
azure_service = AzureOpenAIService()