import asyncio
import unittest
from datetime import datetime
from unittest.mock import patch

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

    def test_list_pr_numbers_full_page(self):
        mocked_full_page = [  # 7 days from 10/10 ~ 10/16
            {
                "number": 7,
                "created_at": "2024-10-16T10:00:00Z",
            },
            {
                "number": 6,
                "created_at": "2024-10-15T10:00:00Z",
            },
            {
                "number": 5,
                "created_at": "2024-10-14T10:00:00Z",
            },
            {
                "number": 4,
                "created_at": "2024-10-13T10:00:00Z",
            },
            {
                "number": 3,
                "created_at": "2024-10-12T10:00:00Z",
            },
            {
                "number": 2,
                "created_at": "2024-10-11T10:00:00Z",
            },
            {
                "number": 1,
                "created_at": "2024-10-10T10:00:00Z",
            },
        ]

        def side_effect(owner, repo, state, sort, direction, per_page, page):
            if page == 1:
                return mocked_full_page
            else:
                return []

        self.mock_api.pulls.list.side_effect = side_effect

        # start and end cover the entire 7 days
        start = datetime.strptime("2024-10-09T10:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end = datetime.strptime("2024-10-17T10:00:00Z", "%Y-%m-%dT%H:%M:%SZ")

        pr_numbers = asyncio.run(
            self.github_provider.list_pr_numbers("test_repo", start, end, True)
        )

        self.assertSequenceEqual(pr_numbers, [7, 6, 5, 4, 3, 2, 1])
        self.mock_api.pulls.list.assert_any_call(
            owner="test_owner",
            repo="test_repo",
            state="closed",
            sort="created",
            direction="desc",
            per_page=100,
            page=1,
        )

    def test_list_pr_numbers_two_pages(self):
        mocked_1st_page = [
            {
                "number": 7,
                "created_at": "2024-10-16T10:00:00Z",
            },
            {
                "number": 6,
                "created_at": "2024-10-15T10:00:00Z",
            },
            {
                "number": 5,
                "created_at": "2024-10-14T10:00:00Z",
            },
            {
                "number": 4,
                "created_at": "2024-10-13T10:00:00Z",
            },
        ]

        mocked_2nd_page = [
            {
                "number": 3,
                "created_at": "2024-10-12T10:00:00Z",
            },
            {
                "number": 2,
                "created_at": "2024-10-11T10:00:00Z",
            },
            {
                "number": 1,
                "created_at": "2024-10-10T10:00:00Z",
            },
        ]

        def side_effect(owner, repo, state, sort, direction, per_page, page):
            if page == 1:
                return mocked_1st_page
            if page == 2:
                return mocked_2nd_page
            else:
                return []

        self.mock_api.pulls.list.side_effect = side_effect

        # start and end cover the entire 7 days
        start = datetime.strptime("2024-10-09T10:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end = datetime.strptime("2024-10-17T10:00:00Z", "%Y-%m-%dT%H:%M:%SZ")

        pr_numbers = asyncio.run(
            self.github_provider.list_pr_numbers("rest_repo", start, end, True)
        )
        self.assertSequenceEqual(pr_numbers, [7, 6, 5, 4, 3, 2, 1])

    def test_list_pr_numbers_only_2nd_page(self):
        mocked_1st_page = [
            {
                "number": 7,
                "created_at": "2024-10-16T10:00:00Z",
            },
            {
                "number": 6,
                "created_at": "2024-10-15T10:00:00Z",
            },
            {
                "number": 5,
                "created_at": "2024-10-14T10:00:00Z",
            },
            {
                "number": 4,
                "created_at": "2024-10-13T10:00:00Z",
            },
        ]

        mocked_2nd_page = [
            {
                "number": 3,
                "created_at": "2024-10-12T10:00:00Z",
            },
            {
                "number": 2,
                "created_at": "2024-10-11T10:00:00Z",
            },
            {
                "number": 1,
                "created_at": "2024-10-10T10:00:00Z",
            },
        ]

        def side_effect(owner, repo, state, sort, direction, per_page, page):
            if page == 1:
                return mocked_1st_page
            if page == 2:
                return mocked_2nd_page
            else:
                return []

        self.mock_api.pulls.list.side_effect = side_effect

        # only covers [10/10 - 10/11] on the 2nd page
        start = datetime.strptime("2024-10-10T10:00:00Z", "%Y-%m-%dT%H:%M:%SZ")
        end = datetime.strptime("2024-10-11T10:00:00Z", "%Y-%m-%dT%H:%M:%SZ")

        pr_numbers = asyncio.run(
            self.github_provider.list_pr_numbers("rest_repo", start, end, True)
        )
        self.assertSequenceEqual(pr_numbers, [2, 1])


if __name__ == "__main__":
    unittest.main()
