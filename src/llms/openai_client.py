import os
from typing import Any, Dict

from openai import OpenAI
from requests.exceptions import RequestException

from .base_client import BaseClient


class OpenAIClient(BaseClient):

    def __init__(self, model: str) -> None:
        self.model = model
        super().__init__()

        key = os.getenv("OPENAI_API_KEY")
        if not key:
            raise RuntimeError("'OPENAI_API_KEY' not found via os.getenv")
        self.client = OpenAI(api_key=key)

    def chat_completion(
        self,
        system: str,
        user: str,
        **kwargs
    ) -> str:
        """
        Generates a completion for a chat interaction using the OpenAI API.

        Args:
            system (str): The system's message or instructions that provide context
                for the conversation. This can include system prompts or setup messages.
            user (str): The user's message or query in the conversation.
            **kwargs: Additional keyword arguments to modify the API request,
                such as 'temperature' to adjust randomness or 'stream' for real-time streaming.

        Returns:
            str: The content of the generated response from the AI model.

        Raises:
            RuntimeError: If there's an issue with the API key being unavailable
                or if communication with the LLM platform fails due to a RequestException.
        """

        try:
            response = self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                **self._load_kwargs(kwargs),
            )
        except RequestException as e:
            raise RuntimeError(f"Failed to communicate with the LLM platform: {str(e)}")

        return response.choices[0].message.content  # type: ignore

    def _load_kwargs(self, kwargs) -> Dict[str, Any]:
        # essential parameters
        kwargs["model"] = self.model

        # default parameter
        if "temperature" not in kwargs:
            kwargs["temperature"] = 0
        if "stream" not in kwargs:
            kwargs["stream"] = False

        return kwargs
