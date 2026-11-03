"""
OpenAI model provider implementation.
Uses the `openai` package to call the ChatCompletion endpoint.
"""

import openai
from .base import ModelProvider
from ..config import load_config
from ..logger import logger


class OpenAIProvider(ModelProvider):
    def __init__(self):
        cfg = load_config()
        api_key = cfg.get("openai_api_key")
        if not api_key:
            raise ValueError("OpenAI API key is missing in config.json")
        openai.api_key = api_key
        self.model = cfg.get("openai_model", "gpt-3.5-turbo")

    def generate(self, prompt: str) -> str:
        logger.debug(f"Sending prompt to OpenAI (model={self.model}): {prompt}")
        response = openai.ChatCompletion.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
        )
        answer = response.choices[0].message["content"]
        logger.debug(f"OpenAI response: {answer}")
        return answer.strip()

    def close(self):
        # No persistent connection to close for OpenAI API
        pass
