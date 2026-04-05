from openai import OpenAI
import os
import json
from loguru import logger
from typing import Optional

class LLMClient:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("LLM_BASE_URL", None) # Let it fallback to OpenAI default
        if not api_key:
            logger.warning("OPENAI_API_KEY is missing. Depending on base_url, requests may fail.")
            
        self.client = OpenAI(
            api_key=api_key or "local-api-key",
            base_url=base_url if base_url else None
        )

    def generate(self, prompt: str, system_prompt: str = "You are a helpful assistant.", model: str = "gpt-4o-mini", json_mode: bool = False) -> str:
        """
        Generates text using the configured LLM. Supports json_mode with compatible models.
        """
        try:
            kwargs = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.2
            }
            if json_mode:
                # We assume the model explicitly supports json_object type
                kwargs["response_format"] = {"type": "json_object"}

            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            raise

    def generate_json(self, prompt: str, system_prompt: str, model: str) -> dict:
        """
        Utility abstraction to always guarantee a dictionary payload response.
        If the model or provider doesn't support JSON mode perfectly, falls back to parsing string output.
        """
        raw_output = self.generate(prompt, system_prompt, model, json_mode=True)
        try:
            return json.loads(raw_output)
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON from LLM output. Attempting cleanup.")
            # Fallback naive cleanup
            cleaned = raw_output.replace("```json", "").replace("```", "").strip()
            return json.loads(cleaned)
