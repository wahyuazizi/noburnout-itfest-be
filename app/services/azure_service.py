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
    
    async def create_summary(self, transcript_text: str, max_tokens: int = 500) -> str:
        """
        Create a summary of the transcript text.
        
        Args:
            transcript_text: The full transcript text to summarize
            max_tokens: Maximum tokens for the summary
            
        Returns:
            Summary text
        """
        try:
            system_prompt = """Anda adalah seorang ahli dalam membuat ringkasan yang ringkas dan informatif. 
            Buat ringkasan transkrip yang jelas dan komprehensif yang mencakup:
            - Topik utama dan poin-poin penting yang dibahas
            - Wawasan atau kesimpulan penting
            - Poin-poin penting bagi audiens
            
            Jaga agar ringkasan terstruktur dengan baik dan mudah dibaca. Berikan ringkasan dalam Bahasa Indonesia."""
            
            user_prompt = f"Mohon buatkan ringkasan dari transkrip ini dalam Bahasa Indonesia:\n\n{transcript_text}"
            
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error creating summary: {str(e)}")
            raise Exception(f"Failed to create summary: {str(e)}")
    
    async def create_study_plan(self, transcript_text: str, study_duration: Optional[str] = "1 week") -> str:
        """
        Create a structured study plan based on the transcript content.
        
        Args:
            transcript_text: The full transcript text to create study plan from
            study_duration: Duration for the study plan (e.g., "1 week", "2 weeks", "1 month")
            
        Returns:
            Structured study plan text
        """
        try:
            system_prompt = f"""You are an expert educational consultant who creates effective study plans. 
            Based on the provided transcript, create a comprehensive {study_duration} study plan that includes:
            
            1. **Learning Objectives** - Clear, measurable goals
            2. **Daily/Weekly Schedule** - Structured timeline for {study_duration}
            3. **Key Topics Breakdown** - Main subjects to focus on
            4. **Study Activities** - Specific tasks and exercises
            5. **Review Sessions** - Spaced repetition and practice
            6. **Assessment Methods** - Ways to test understanding
            7. **Additional Resources** - Suggested supplementary materials
            
            Make the study plan practical, achievable, and well-organized. 
            Use clear headings and bullet points for easy following."""
            
            user_prompt = f"""Create a {study_duration} study plan based on this transcript content:

{transcript_text}

Please make it detailed and actionable."""
            
            response = await self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1500,
                temperature=0.4
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error creating study plan: {str(e)}")
            raise Exception(f"Failed to create study plan: {str(e)}")

# Create service instance
azure_service = AzureOpenAIService()