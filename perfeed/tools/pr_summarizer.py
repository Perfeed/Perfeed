import asyncio
import json

import requests
from jinja2 import Environment, StrictUndefined

from perfeed.config_loader import settings
from perfeed.git_providers.base import BaseGitProvider
from perfeed.git_providers.github import GithubProvider
from perfeed.llms.base_client import BaseClient
from perfeed.models.pr_summary import PRSummary, PRSummaryMetadata
from perfeed.utils import json_output_curator
from datetime import datetime, timezone
from typing import Tuple
from collections import defaultdict
from perfeed.models.git_provider import PRComment

class PRSummarizer:
    def __init__(self, git: BaseGitProvider, llm: BaseClient):
        self.git = git
        self.llm = llm

    async def run(
        self, repo: str, pr_number: int
    ) -> Tuple[PRSummary, PRSummaryMetadata]:
        pr = await self.git.get_pr(repo, pr_number)

        self.variables = {
            "author": pr.author,
            "title": pr.title,
            "description": pr.description,
            "code": requests.get(pr.diff_url).text,
            "comments": self._comments_to_thread(pr.comments),
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
        print(curated_summary) 
        pr_summary = PRSummary(**json.loads(curated_summary))
        current_time = datetime.now(timezone.utc)
        pr_metadata = PRSummaryMetadata(
            repo=repo,
            author=pr.author,
            pr_number=pr_number,
            llm_provider=self.llm.__class__.__name__,
            model=self.llm.model,
            pr_created_at=pr.created_at,
            pr_merged_at=pr.merged_at,
            created_at=current_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        return pr_summary, pr_metadata

    
    def _comments_to_thread(self, pr_comments: list[PRComment]) -> str:
        thread = defaultdict()
        for prc in pr_comments:
            if not prc.in_reply_to_id:
                thread[prc.id] = {
                    'parent_thread_id': prc.id,
                    'child_thread_ids': [],
                    'diff_hunk': prc.diff_hunk,
                    'html_url': prc.html_url,
                    'content': [
                        {
                            'user': prc.user,
                            'body': prc.body,
                            'created_at': prc.created_at
                        }
                    ],
                    'code_change': prc.code_change
                }
            else:
                thread[prc.in_reply_to_id]['child_thread_ids'].append(prc.id)
                thread[prc.in_reply_to_id]['content'].append(
                    {
                        'user': prc.user,
                        'body': prc.body,
                        'created_at': prc.created_at
                    }
                )

        return json.dumps([i for i in thread.values()])


if __name__ == "__main__":
    from perfeed.llms.ollama_client import OllamaClient
    from perfeed.llms.openai_client import OpenAIClient

    summarizer = PRSummarizer(
        GithubProvider("Perfeed"), llm=OllamaClient("llama3.1")
    )
    # summarizer = PRSummarizer(GithubProvider("Perfeed"), llm=OpenAIClient("gpt-4o-mini"))
    pr_summary = asyncio.run(summarizer.run("perfeed", 14))
    print(pr_summary)
