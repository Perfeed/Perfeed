import asyncio
import unittest
from unittest.mock import patch
from datetime import datetime

from perfeed.git_providers.github import GithubProvider
from perfeed.models.git_provider import CommentType, PRComment, PullRequest


class TestGithubProvider(unittest.TestCase):

    @patch("perfeed.git_providers.github.GhApi")
    def setUp(self, MockGhApi):
        """
        Set up a mock GithubProvider instance before each test.
        """
        self.mock_api = MockGhApi.return_value
        self.github_provider = GithubProvider(owner="test_owner", token="fake_token")

    def test_get_pr_comments_issue_comment(self):
        """
        Test _get_pr_comments with issue comments.
        """
        self.mock_api.issues.list_comments.return_value = [
            {
                "id": 1,
                "user": {"login": "test_user", "type": "User"},
                "created_at": "2023-10-01T10:00:00Z",
                "body": "Test issue comment",
                "html_url": "http://example.com/comment/1",
            }
        ]

        comments = asyncio.run(
            self.github_provider._get_pr_comments(
                "test_owner", "test_repo", 1, CommentType.ISSUE_COMMENT
            )
        )

        self.assertEqual(len(comments), 1)
        self.assertIsInstance(comments[0], PRComment)
        self.assertEqual(comments[0].body, "Test issue comment")

    def test_get_pr_comments_review_comment(self):
        """
        Test _get_pr_comments with review comments.
        """
        self.mock_api.pulls.list_review_comments.return_value = [
            {
                "id": 2,
                "user": {"login": "review_user", "type": "User"},
                "created_at": "2023-10-01T11:00:00Z",
                "body": "Test review comment",
                "html_url": "http://example.com/comment/2",
            }
        ]

        comments = asyncio.run(
            self.github_provider._get_pr_comments(
                "test_owner", "test_repo", 1, CommentType.REVIEW_COMMENT
            )
        )

        self.assertEqual(len(comments), 1)
        self.assertIsInstance(comments[0], PRComment)
        self.assertEqual(comments[0].body, "Test review comment")

    def test_list_pr_comments(self):
        """
        Test list_pr_comments to ensure it combines and sorts issue and review comments.
        """
        self.mock_api.issues.list_comments.return_value = [
            {
                "id": 1,
                "user": {"login": "test_user", "type": "User"},
                "created_at": "2023-10-01T10:00:00Z",
                "body": "Issue comment",
                "html_url": "http://example.com/comment/1",
            }
        ]
        self.mock_api.pulls.list_review_comments.return_value = [
            {
                "id": 2,
                "user": {"login": "review_user", "type": "User"},
                "created_at": "2023-10-01T11:00:00Z",
                "body": "Review comment",
                "html_url": "http://example.com/comment/2",
            }
        ]

        comments = asyncio.run(self.github_provider.list_pr_comments("test_repo", 1))

        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0].created_at, "2023-10-01T10:00:00Z")
        self.assertEqual(comments[1].created_at, "2023-10-01T11:00:00Z")

    def test_fetch_pr(self):
        """
        Test fetch_pr method to ensure it fetches and converts PR data.
        """
        pr_data = {
            "number": 123,
            "title": "Test PR",
            "user": {"login": "author"},
            "state": "open",
            "created_at": "2023-10-01T10:00:00Z",
            "body": "This is a test pull request.",
            "html_url": "http://example.com/pr/123",
            "diff_url": "http://example.com/diff",
            "additions": 10,
            "deletions": 5,
            "merged_at": None,
        }

        # Mock the API response for fetch_pr method
        self.mock_api.pulls.get.return_value = pr_data

        # Patch _to_PullRequest method within github_provider instance
        with patch.object(
            self.github_provider,
            "_to_PullRequest",
            return_value=PullRequest(
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
            ),
        ) as mock_to_pull_request:
            asyncio.run(self.github_provider.get_pr("test_repo", 123))
            mock_to_pull_request.assert_called_once_with(pr_data)

    @patch("perfeed.git_providers.github.GithubProvider._get_pr_comments")
    def test_to_PullRequest(self, mock_get_pr_comments):
        """
        Test _to_PullRequest method to ensure it converts PR data correctly.
        """
        pr_data = {
            "number": 123,
            "title": "Test PR",
            "user": {"login": "author"},
            "base": {"repo": {"name": "test_repo"}},
            "state": "open",
            "created_at": "2023-10-01T10:00:00Z",
            "body": "This is a test pull request.",
            "html_url": "http://example.com/pr/123",
            "diff_url": "http://example.com/diff",
            "additions": 10,
            "deletions": 5,
            "merged_at": None,
        }

        self.mock_api.pulls.list_commits.return_value = [
            {"commit": {"author": {"date": "2023-09-30T10:00:00Z"}}}
        ]
        self.mock_api.pulls.list_reviews.return_value = [
            {"user": {"login": "reviewer1", "type": "User"}}
        ]
        mock_get_pr_comments.return_value = []

        pull_request = asyncio.run(self.github_provider._to_PullRequest(pr_data))

        self.assertEqual(pull_request.title, "Test PR")
        self.assertEqual(pull_request.diff_lines, "+10 -5")
        self.assertEqual(pull_request.reviewers, ["reviewer1"])
    
    @patch("perfeed.git_providers.github.GithubProvider._fetch_pr_numbers")
    async def test_get_authors_repo_prs(self, mock_fetch_pr_numbers):
        """
        Test get_authors_repo_prs to ensure it returns PRs grouped by author and repository.
        """
        # Mock PR data for two repositories
        mock_fetch_pr_numbers.side_effect = [
            [
                {"number": 1, "user": {"login": "author1"}},
                {"number": 2, "user": {"login": "author2"}},
            ],
            [
                {"number": 3, "user": {"login": "author1"}},
                {"number": 4, "user": {"login": "author2"}},
            ]
        ]

        # Mock the list of repositories returned by the API
        self.mock_api.repos.list_for_org.return_value = [
            {"name": "repo1"},
            {"name": "repo2"}
        ]

        # Define the date range and authors
        start_date = datetime.strptime("2023-10-01", "%Y-%m-%d")
        end_date = datetime.strptime("2023-10-31", "%Y-%m-%d")
        authors = ["author1", "author2"]

        # Call the function
        result = await self.github_provider.get_authors_repo_prs(authors=authors, start_date=start_date, end_date=end_date)

        # Assert the structure of the result
        self.assertEqual(len(result), 2)

        # Check data for author1
        author1_data = next(item for item in result if item.author == "author1")
        self.assertEqual(len(author1_data.repository_pull_requests), 2)
        self.assertEqual(author1_data.repository_pull_requests[0].repository_name, "repo1")
        self.assertEqual(author1_data.repository_pull_requests[0].pull_request_number, [1])
        self.assertEqual(author1_data.repository_pull_requests[1].repository_name, "repo2")
        self.assertEqual(author1_data.repository_pull_requests[1].pull_request_number, [3])

        # Check data for author2
        author2_data = next(item for item in result if item.author == "author2")
        self.assertEqual(len(author2_data.repository_pull_requests), 2)
        self.assertEqual(author2_data.repository_pull_requests[0].repository_name, "repo1")
        self.assertEqual(author2_data.repository_pull_requests[0].pull_request_number, [2])
        self.assertEqual(author2_data.repository_pull_requests[1].repository_name, "repo2")
        self.assertEqual(author2_data.repository_pull_requests[1].pull_request_number, [4])

    @patch("perfeed.git_providers.github.GithubProvider._fetch_pr_numbers")
    async def test_get_authors_repo_prs_no_prs(self, mock_fetch_pr_numbers):
        """
        Test get_authors_repo_prs to handle the case where no PRs are returned.
        """
        # Mock no PR data (empty list)
        mock_fetch_pr_numbers.side_effect = [[], []]

        # Mock the list of repositories returned by the API
        self.mock_api.repos.list_for_org.return_value = [
            {"name": "repo1"},
            {"name": "repo2"}
        ]

        # Define the date range and authors
        start_date = datetime.strptime("2023-10-01", "%Y-%m-%d")
        end_date = datetime.strptime("2023-10-31", "%Y-%m-%d")
        authors = ["author1", "author2"]

        # Call the function
        result = await self.github_provider.get_authors_repo_prs(authors=authors, start_date=start_date, end_date=end_date)

        # Assert that the result is empty
        self.assertEqual(len(result), 0)


if __name__ == "__main__":
    unittest.main()
