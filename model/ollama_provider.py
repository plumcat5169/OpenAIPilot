"""
Ollama model provider implementation.
Communicates with a local Ollama server via its HTTP API.
"""

import json
import requests
from .base import ModelProvider
from ..config import load_config
from ..logger import logger


class OllamaProvider(ModelProvider):
    def __init__(self):
        cfg = load_config()
        self.base_url = cfg.get("ollama_url", "http://127.0.0.1:11434")
        self.model = cfg.get("ollama_model", "mistral")

    def generate(self, prompt: str) -> str:
        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7},
        }
        logger.debug(f"Sending prompt to Ollama (model={self.model}): {prompt}")
        try:
            resp = requests.post(endpoint, json=payload, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            answer = data.get("response", "")
            logger.debug(f"Ollama response: {answer}")
            return answer.strip()
        except requests.RequestException as e:
            logger.error(f"Error communicating with Ollama: {e}")
            raise

    def close(self):
        # No persistent connection to close for Ollama HTTP API
        pass
