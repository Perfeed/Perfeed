import unittest

from perfeed.models.git_provider import CommentType, PRComment, PullRequest
from perfeed.git_providers.github import comments_to_thread
import json


class TestGithubCommentsToThread(unittest.TestCase):
    def test_threaded_comments(self):
        comments = [
            PRComment(
                id=1,
                type=CommentType.ISSUE_COMMENT,
                user="user1",
                user_type="User",
                diff_hunk="@@ -1 +1 @@",
                body="This is the first comment.",
                created_at="2023-10-01T10:00:00Z",
                code_change=True,
                in_reply_to_id=None,
                html_url="test.com"
            ),
            PRComment(
                id=2,
                type=CommentType.ISSUE_COMMENT,
                user="user2",
                user_type="User",
                diff_hunk="@@ -1 +1 @@",
                body="This is the replied comment to the first comment - id1.",
                created_at="2023-10-02T10:00:00Z",
                code_change=True,
                in_reply_to_id=1,
                html_url="test.com"
            ),
            PRComment(
                id=3,
                type=CommentType.ISSUE_COMMENT,
                user="user3",
                user_type="User",
                diff_hunk="@@ -5 +5 @@",
                body="This is a third comment unrelated to previous 2.",
                created_at="2023-10-03T10:00:00Z",
                code_change=False,
                in_reply_to_id=None,
                html_url="test.com"
            )

        ]
        result = comments_to_thread(comments)
        expected = json.dumps(
            [
                {
                    'parent_thread_id': 1,
                    'child_thread_ids': [2],
                    'diff_hunk': '@@ -1 +1 @@',
                    'html_url': 'test.com',
                    'content': [
                        {'user': 'user1',
                        'body': 'This is the first comment.',
                        'created_at': '2023-10-01T10:00:00Z'},
                        {'user': 'user2',
                        'body': 'This is the replied comment to the first comment - id1.',
                        'created_at': '2023-10-02T10:00:00Z'}
                    ],
                    'code_change': True
                },
                {
                    'parent_thread_id': 3,
                    'child_thread_ids': [],
                    'diff_hunk': '@@ -5 +5 @@',
                    'html_url': 'test.com',
                    'content': [
                        {'user': 'user3',
                        'body': 'This is a third comment unrelated to previous 2.',
                        'created_at': '2023-10-03T10:00:00Z'}
                    ],
                    'code_change': False
                }
            ]
        )
        self.assertEqual(result, expected)



if __name__ == "__main__":
    unittest.main()