import ollama
from .base_client import BaseClient
from typing import Dict, Any

class OllamaClient(BaseClient):
    def __init__(
            self,
            model: str,
            **kwargs
    ):
        self.model = model
        self.all_kwargs = self._load_kwargs(kwargs)
        super().__init__()

    def chat_completion(
        self, system: str, user: str,
    ) -> str:

        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            options=self.all_kwargs,
        )

        return response["message"]["content"]

    def _load_kwargs(self, kwargs):
        if 'num_ctx' not in kwargs:
            kwargs['num_ctx'] = 4096
        if 'temperature' not in kwargs:
            kwargs['temperature'] = 0
        return kwargs
