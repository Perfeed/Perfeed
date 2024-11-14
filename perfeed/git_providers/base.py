from abc import ABC, abstractmethod
from datetime import datetime

from perfeed.models.git_provider import PRComment, PullRequest


class BaseGitProvider(ABC):

    @abstractmethod
    def __init__(self, owner: str, token: str | None = None):
        pass

    @abstractmethod
    async def list_pr_comments(self, repo_name: str, pr_number: int) -> list[PRComment]:
        pass

    @abstractmethod
    async def get_pr(self, repo: str, pr_number: int) -> PullRequest:
        pass

    @abstractmethod
    async def search_prs(
        self,
        repo_name: str,
        start_date: datetime,
        end_date: datetime,
        authors: set[str],
        closed_only: bool = True,
    ) -> list[int]:
        pass
