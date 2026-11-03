"""
Abstract base class for model providers.
All concrete providers must implement `generate(prompt: str) -> str` and `close()`.
"""

from abc import ABC, abstractmethod


class ModelProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Send a prompt to the model and return its response as a string."""
        pass

    @abstractmethod
    def close(self):
        """Release any resources held by the provider (if needed)."""
        pass
