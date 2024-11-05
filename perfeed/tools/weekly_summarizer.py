import asyncio
import time
from datetime import datetime, timedelta

from jinja2 import Environment, StrictUndefined

from perfeed.config_loader import settings
from perfeed.git_providers.base import BaseGitProvider
from perfeed.git_providers.github import GithubProvider
from perfeed.llms.base_client import BaseClient
from perfeed.llms.ollama_client import OllamaClient
from perfeed.models.pr_summary import PRSummary
from perfeed.tools.pr_summarizer import PRSummarizer
from perfeed.utils.utils import json_output_curator


# python perfeed.py -users jimmytai chihangwang -repo perfeed-backend -period 1w
class WeeklySummarizer:
    def __init__(self, git: BaseGitProvider, summarizer: PRSummarizer, llm: BaseClient):
        self.git = git
        self.summarizer = summarizer
        self.llm = llm

    async def run(self, users: list[str], repo_name: str, start_of_week: str) -> None:

        # Check if start_of_week must be the Sunday or Monday of the week
        try:
            date = datetime.strptime(start_of_week, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Invalid date format. Please use 'YYYY-MM-DD'.")

        # Check if the day of the week is Monday (0) or Sunday (-1)
        if date.weekday() not in [0, 6]:
            raise ValueError("Start day must be a Sunday or Monday.")

        # Use local timezone by default
        start_date = date.astimezone()
        end_date = start_date + timedelta(days=6)

        print(f"Summarizing {repo_name} for {users} from {start_date} to {end_date}")

        now = time.perf_counter()
        # TODO: filter results by users
        pr_numbers = await self.git.list_pr_numbers(
            repo_name, start_date, end_date, True
        )

        print(f"Summarizing the following PR-{pr_numbers}")

        # TODO: load the PR summaries from the pervious batch if exists.

        summary_futures = [
            self.summarizer.run(repo_name, pr_number) for pr_number in pr_numbers
        ]

        summaries = await asyncio.gather(*summary_futures, return_exceptions=True)

        elapsed = time.perf_counter() - now
        print(f"Summarized {len(summaries)} PRs in {elapsed:0.5f} seconds")

        # TODO: store PRSummary results so we don't have to re-process again

        # TODO: handle failed summary futures with BaseException
        json_summaries = [
            summary.model_dump_json()
            for summary in summaries
            if not isinstance(summary, BaseException)
        ]

        self.variables = {
            "PRSummary": PRSummary.to_json_schema(),
            "pr_summaries": json_summaries,
        }

        environment = Environment(undefined=StrictUndefined)
        system_prompt = environment.from_string(
            settings.weekly_summary_prompt.system
        ).render(self.variables)
        user_prompt = environment.from_string(
            settings.weekly_summary_prompt.user
        ).render(self.variables)

        summary = self.llm.chat_completion(system_prompt, user_prompt)
        curated_summary = json_output_curator(summary)

        print(f"Summary of the Week: \n{curated_summary}\n")


if __name__ == "__main__":
    git = GithubProvider("Perfeed")
    summarizer = PRSummarizer(git=git, llm=OllamaClient("llama3.1:8b"))
    llm = OllamaClient("llama3.1:8b")
    weekly_summarizer = WeeklySummarizer(git=git, summarizer=summarizer, llm=llm)
    asyncio.run(
        weekly_summarizer.run(
            users=["jimmytai", "chihangwang"],
            repo_name="perfeed",
            start_of_week="2024-10-21",
        )
    )
