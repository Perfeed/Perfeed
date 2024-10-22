from abc import ABC, abstractmethod
from datetime import datetime

from perfeed.models.git_provider import PRComment, PullRequest


class BaseGitProvider(ABC):

    @abstractmethod
    def __init__(self, owner: str, token: str | None = None):
        pass

    @abstractmethod
    def list_pr_comments(self, repo_name: str, pr_number: int) -> list[PRComment]:
        pass

    @abstractmethod
    def get_pr(self, repo: str, pr_number: int) -> PullRequest:
        pass

    @abstractmethod
    def list_pr_numbers(
        self, owner: str, repo_name: str, start_date: datetime, end_date: datetime
    ) -> list[int]:
        pass
