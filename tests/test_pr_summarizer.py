import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from perfeed.git_providers.base import BaseGitProvider
from perfeed.git_providers.github import GithubProvider
from perfeed.llms.base_client import BaseClient
from perfeed.llms.ollama_client import OllamaClient
from perfeed.models.git_provider import PullRequest
from perfeed.tools.pr_summarizer import PRSummarizer


class TestPRSummarizer(unittest.IsolatedAsyncioTestCase):

    @patch("perfeed.tools.pr_summarizer.BaseGitProvider")
    @patch("perfeed.tools.pr_summarizer.BaseClient")
    def test_run(self, mock_llm, mock_git_provider) -> None:
        async_mocked_pr = AsyncMock()
        async_mocked_pr.return_value = PullRequest(
            number=123,
            title="Test PR",
            state="open",
            author="author",
            reviewers=["reviewer1"],
            created_at="2023-10-01T10:00:00Z",
            first_committed_at="2023-09-30T10:00:00Z",
            description="This is a test pull request.",
            html_url="http://example.com/pr/123",
            diff_url="http://example.com/diff",
            comments=[],
            diff_lines="+10 -5",
            merged_at=None,
        )
        mock_git_provider.get_pr.return_value = async_mocked_pr

        summarizer = PRSummarizer(mock_git_provider, mock_llm)
        asyncio.run(summarizer.run("Test Repo", 123))
