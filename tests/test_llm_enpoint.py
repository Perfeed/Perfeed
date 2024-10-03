import unittest
from unittest.mock import patch, MagicMock
from src.utils.llm_endpoint import LLM


class TestLLM(unittest.TestCase):
    @patch('src.utils.llm_endpoint.LLM')
    def test_platform_with_key(self, MockLLM):
        mock_client = MagicMock()
        MockLLM.return_value = mock_client

        llm_openai = LLM(platform='openai', model_name='gpt-3', key='dummy_key')
        self.assertIsNotNone(llm_openai.client)
        self.assertEqual(llm_openai.key, 'dummy_key')

        llm_ollama = LLM(platform='ollama', model_name='llama3', key='dummy_key')
        self.assertIsNotNone(llm_openai.client)
        self.assertEqual(llm_ollama.key, 'dummy_key')

        llm_openrouter = LLM(platform='openrouter', model_name='llama3', key='dummy_key')
        self.assertIsNotNone(llm_openai.client)
        self.assertEqual(llm_openrouter.key, 'dummy_key')

    def test_openai_platform_without_key(self):
        with self.assertRaises(RuntimeError) as context:
            LLM(platform='openai', model_name='gpt-3')
        self.assertIn("'OPENAI_API_KEY' not found via os.getenv", str(context.exception))

    def test_invalid_platform(self):
        with self.assertRaises(RuntimeError) as context:
            LLM(platform='invalid_platform', model_name='llama9')
        self.assertIn('platform "invalid_platform" not recognized/supported.', str(context.exception))


if __name__ == '__main__':
    unittest.main()
