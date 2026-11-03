"""
Ollama Cloud API provider implementation (local‑style endpoint).
"""

import json
import requests
from .base import ModelProvider
from ..config import load_config
from ..logger import logger


class OllamaCloudProvider(ModelProvider):
    def __init__(self):
        cfg = load_config()
        self.api_key = cfg.get("ollama_api_key")
        if not self.api_key:
            raise ValueError("Ollama Cloud API key is missing in config.json (ollama_api_key)")
        # Base URL may be either "https://ollama.com" or "https://api.ollama.com"
        self.base_url = cfg.get("ollama_cloud_url", "https://ollama.com")
        self.model = cfg.get("ollama_model", "mistral")
        # Normalize base URL to ensure we don't duplicate /api
        base = self.base_url.rstrip("/")
        if not base.endswith("/api"):
            self.generate_endpoint = f"{base}/api/generate"
        else:
            self.generate_endpoint = f"{base}/generate"

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    def generate(self, prompt: str) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": (
                "You are a local PC assistant embedded in a Python program. "
                "When the user asks to open, launch, type, or perform actions on their computer, "
                "reply with a single line that starts exactly with 'COMMAND:' followed by the "
                "action in plain English (e.g., 'COMMAND: open telegram', 'COMMAND: type hello'). "
                "If you cannot perform an action, politely explain why."
            ),
            "stream": False,
            "options": {"temperature": 0.7},
        }
        logger.debug(f"Sending request to Ollama Cloud at {self.generate_endpoint}")
        try:
            response = requests.post(self.generate_endpoint, headers=self._headers(), json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            answer = data.get("response", "")
            logger.debug(f"Ollama Cloud response: {answer}")
            return answer.strip()
        except requests.RequestException as e:
            logger.error(f"Error communicating with Ollama Cloud API: {e}")
            raise

    def close(self):
        pass
