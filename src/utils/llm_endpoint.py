import os
from openai import OpenAI
from requests.exceptions import RequestException


class LLM:

    def __init__(self, platform: str, model_name: str, key: str):
        self.platform = platform
        self.model_name = model_name
        self.key = key
        if self.platform == 'openai':
            if not self.key:
                self.key = os.getenv('OPENAI_API_KEY')
                if not self.key:
                    raise RuntimeError("'OPENAI_API_KEY' not found via os.getenv" )
            self.client = OpenAI(
                api_key=self.key
            )

        elif self.platform == 'openrouter':
            if not self.key:
                self.key = os.getenv('OPENROUTER_API_KEY')
                if not self.key:
                    raise RuntimeError("'OPENROUTER_API_KEY' not found via os.getenv" )
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.key,
            )
        elif self.platform == 'ollama':
            self.client = OpenAI(
                base_url='http://localhost:11434/v1',
                api_key="ollama"
            )
        else:
            raise RuntimeError(f'platform "{self.platform}" not recognized/supported.')

    def invoke(self, user_prompt: str, system_prompt: str="") -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ]
            )
        except RequestException as e:
            raise RuntimeError(f"Failed to communicate with the LLM platform: {str(e)}")

        return response.choices[0].message.content
