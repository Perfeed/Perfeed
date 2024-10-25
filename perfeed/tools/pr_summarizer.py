import json
import asyncio
import requests
from jinja2 import Environment, StrictUndefined

from perfeed.config_loader import settings
from perfeed.git_providers import github
from perfeed.llms.base_client import BaseClient
from perfeed.llms.ollama_client import OllamaClient
from perfeed.models.pr_summary import PRSummary
from perfeed.utils import json_output_curator

class PRSummarizer:
    def __init__(self, owner: str, llm: BaseClient):
        self.git = github.GithubProvider(owner=owner)
        self.llm = llm

    def run(self, repo: str, pr_number: int) -> PRSummary:
        pr = asyncio.run(self.git.get_pr(repo, pr_number))

        self.variables = {
            "author": pr.author,
            "title": pr.title,
            "description": pr.description,
            "code": requests.get(pr.diff_url).text,
            "comments": pr.to_dict()["comments"],
            "PRSummary": PRSummary.to_json_schema(),
        }

        environment = Environment(undefined=StrictUndefined)
        system_prompt = environment.from_string(
            settings.pr_summary_prompt.system
        ).render(self.variables)
        user_prompt = environment.from_string(settings.pr_summary_prompt.user).render(
            self.variables
        )

        summary = self.llm.chat_completion(system_prompt, user_prompt)
        curated_summary = json_output_curator(summary)
        pr_summary = PRSummary(**json.loads(curated_summary))
        return pr_summary


if __name__ == "__main__":
    summarizer = PRSummarizer(owner="Perfeed", llm=OllamaClient("llama3.2"))
    pr_summary = summarizer.run("perfeed", 5)
    print(pr_summary)
