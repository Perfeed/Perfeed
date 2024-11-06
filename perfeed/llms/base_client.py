from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class BaseClient(ABC):
    """
    This class defines the interface for a LLM client.
    """
    model: str

    @abstractmethod
    def chat_completion(self, system: str, user: str, **kwargs) -> str:
        """
        This method should be implemented to return a chat completion from the AI model.
        Args:
            model (str): the name of the model to use for the chat completion
            system (str): the system message string to use for the chat completion
            user (str): the user message string to use for the chat completion

        Returns: the chat completion response
        """
        pass
