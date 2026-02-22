import asyncio
from concurrent.futures import ThreadPoolExecutor
from deep_translator import GoogleTranslator
from google import genai
from typing import Optional
import logging
import os
from app.core.config import settings

logger = logging.getLogger(__name__)

class TranslatorService:
    """
    Service to handle language translation for the AgriGPT platform.
    Supports English, Hindi, and Telugu.
    Enhanced with LLM (Gemini) for contextual agricultural translation.
    """
    
    def __init__(self):
        # Cache translators for common language pairs to improve performance
        self.translators = {}
        self.executor = ThreadPoolExecutor(max_workers=5)
        
        # Initialize Gemini client if API key is present
        self.gemini_client = None
        if settings.GOOGLE_API_KEY:
            try:
                self.gemini_client = genai.Client(api_key=settings.GOOGLE_API_KEY)
                logger.info("Gemini client initialized for advanced translation.")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")

    def _get_translator(self, source: str, target: str):
        key = f"{source}_{target}"
        if key not in self.translators:
            self.translators[key] = GoogleTranslator(source=source, target=target)
        return self.translators[key]

    async def translate_text(self, text: str, target_lang: str, source_lang: str = 'auto', use_llm: Optional[bool] = None) -> str:
        """
        Translates text from source language to target language.
        
        ACTS AUTONOMOUSLY: 
        1. If use_llm is passed (True/False), it follows that.
        2. If use_llm is None, it uses the LLM automatically if:
           - GOOGLE_API_KEY is present.
           - The text is more than 3 words (contextual query).
        3. Fallback: Always falls back to standard translator on failure.
        """
        if not text or not text.strip():
            return ""
            
        if source_lang == target_lang:
            return text

        # Determine if we should use LLM autonomously
        should_use_llm = use_llm
        if should_use_llm is None:
            # Autonomous logic: Use LLM if key is present AND it's a real query (not just "hello")
            word_count = len(text.split())
            should_use_llm = self.gemini_client is not None and word_count > 2

        if should_use_llm and self.gemini_client:
            try:
                return await self.translate_text_llm(text, target_lang, source_lang)
            except Exception as e:
                logger.warning(f"Autonomous LLM failed, falling back to standard: {e}")

        # Standard / Fallback translation
        try:
            translator = self._get_translator(source_lang, target_lang)
            loop = asyncio.get_event_loop()
            translated = await loop.run_in_executor(
                self.executor, 
                translator.translate, 
                text
            )
            return translated
        except Exception as e:
            logger.error(f"Translation Error ({source_lang} -> {target_lang}): {e}")
            return text

    async def translate_text_llm(self, text: str, target_lang: str, source_lang: str = 'auto') -> str:
        """
        Uses Gemini LLM for high-accuracy contextual translation.
        Includes a 10-second timeout to prevent service hanging.
        """
        if not self.gemini_client:
            return text

        lang_names = {
            'en': 'English',
            'hi': 'Hindi',
            'te': 'Telugu'
        }
        
        src = lang_names.get(source_lang, source_lang)
        tgt = lang_names.get(target_lang, target_lang)

        prompt = f"""You are a strict technical translator specialized in Agriculture.
Your task is to translate from {src} to {tgt}.

RULES:
1. Output ONLY the translated text. 
2. Do not include phrases like "Here is the translation" or "I can't translate".
3. Maintain technical accuracy for crops, pests, and schemes.
4. If the input is not {src}, just translate it to the best of your ability into {tgt}.

TEXT TO TRANSLATE:
{text}"""

        try:
            # Set a 10s timeout for the LLM response
            response = await asyncio.wait_for(
                asyncio.to_thread(
                    self.gemini_client.models.generate_content,
                    model='gemini-2.0-flash',
                    contents=prompt
                ),
                timeout=10.0
            )
            return response.text.strip()
        except asyncio.TimeoutError:
            logger.error(f"LLM Translation Timeout ({source_lang} -> {target_lang})")
            # Fallback to standard translation
            return await self.translate_text(text, target_lang, source_lang, use_llm=False)
        except Exception as e:
            logger.error(f"LLM Translation Error ({source_lang} -> {target_lang}): {e}")
            # Fallback to normal translation if LLM fails
            return await self.translate_text(text, target_lang, source_lang, use_llm=False)

# Global singleton instance
translator_service = TranslatorService()
