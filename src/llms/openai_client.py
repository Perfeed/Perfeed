import os

from openai import OpenAI
from requests.exceptions import RequestException
from typing import Dict, Any
from .base_client import BaseClient


class OpenAIClient(BaseClient):

    def __init__(
            self,
            model: str,
            **kwargs
    ) -> None:
        self.model = model
        self.all_kwargs = self._load_kwargs(kwargs)
        super().__init__()

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("'OPENAI_API_KEY' not found via os.getenv")
        self.client = OpenAI(api_key=key)

    def chat_completion(
        self, user: str, system: str = "",
    ) -> str:

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                **self.all_kwargs
            )
        except RequestException as e:
            raise RuntimeError(f"Failed to communicate with the LLM platform: {str(e)}")

        return response.choices[0].message.content  # type: ignore

    def _load_kwargs(self, kwargs) -> Dict[str, Any]:
        # essential parameters
        kwargs['model'] = self.model

        # default parameter
        if 'temperature' not in kwargs:
            kwargs['temperature'] = 0
        if 'stream' not in kwargs:
            kwargs['stream'] = False

        return kwargs
