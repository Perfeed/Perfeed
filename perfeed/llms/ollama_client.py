import ollama

from perfeed.config_loader import settings
from perfeed.utils.utils import count_tokens

from .base_client import BaseClient


class OllamaClient(BaseClient):
    def __init__(self, model: str):
        self.model = model

    def chat_completion(self, system: str, user: str, **kwargs) -> str:
        """
        Generate a chat completion response using the specified model.

        This function interacts with the Ollama API to generate a response
        based on input messages from the system and the user. Additional
        parameters can be customized via kwargs.

        Args:
            system (str): The content of the message from the system.
            user (str): The content of the message from the user.
            **kwargs: Optional keyword arguments for additional options:
                - num_ctx (int): The context size for the model, default is 4096.
                - temperature (float): The randomness in the model's output,
                  default is 0.

        Returns:
            str: The content of the generated message response.
        """

        default_num_ctx = settings.ollama.num_ctx
        if settings.ollama.auto_num_ctx:
            approx_token_counts = count_tokens("".join([system, user]))
            num_ctx_buffer = settings.ollama.num_ctx_buffer
            default_num_ctx = int(approx_token_counts * num_ctx_buffer)

        default_temperature = settings.ollama.temperature

        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            options={
                "num_ctx": kwargs.get("num_ctx", default_num_ctx),
                "temperature": kwargs.get("temperature", default_temperature),
            },
        )

        return response["message"]["content"]
