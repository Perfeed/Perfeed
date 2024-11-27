import asyncio
import json
from datetime import datetime, timezone
from typing import Tuple

import requests
from jinja2 import Environment, StrictUndefined

from perfeed.config_loader import settings
from perfeed.data_stores.base import BaseStorage
from perfeed.data_stores.storage_feather import FeatherStorage
from perfeed.git_providers.base import BaseGitProvider
from perfeed.git_providers.github import GithubProvider, comments_to_thread
from perfeed.llms.base_client import BaseClient
from perfeed.log import get_logger
from perfeed.models.pr_summary import PRSummary, PRSummaryMetadata
from perfeed.utils import json_output_curator


class PRSummarizer:
    def __init__(self, git: BaseGitProvider, llm: BaseClient, store: BaseStorage):
        self.git = git
        self.llm = llm
        self.store = store

    async def run(
        self, repo: str, pr_number: int
    ) -> Tuple[PRSummary, PRSummaryMetadata]:
        get_logger().info(f"Summarizing {repo}#{pr_number}")

        pr_summary: PRSummary
        pr_metadata: PRSummaryMetadata

        # load from store and return the previously saved result
        df = self.store.load()
        if df.size > 0 and not df[df["pr_number"] == pr_number].empty:

            if settings.config.strict_load_by_model_provider:
                df = df[
                    (df["llm_provider"] == self.llm.__class__.__name__)
                    & (df["model"] == self.llm.model)
                ]

            df = df[df["created_at"].rank(ascending=False) == 1]

            if not df.empty:
                loaded_json = json.loads(df.to_json(orient="records"))[0]
                pr_summary = PRSummary(**loaded_json)
                pr_metadata = PRSummaryMetadata(**loaded_json)
                get_logger().info(f"Loaded {repo}#{pr_number} from store")
                return pr_summary, pr_metadata

        pr = await self.git.get_pr(repo, pr_number)

        self.variables = {
            "author": pr.author,
            "title": pr.title,
            "description": pr.description,
            "code": requests.get(pr.diff_url).text,
            "comments": comments_to_thread(pr.comments),
            "PRSummary": PRSummary.to_json_schema(),
        }

        environment = Environment(undefined=StrictUndefined)
        system_prompt = environment.from_string(
            settings.pr_summary_prompt.system
        ).render(self.variables)
        # get_logger().debug(f"system_prompt: \n{system_prompt}")

        user_prompt = environment.from_string(settings.pr_summary_prompt.user).render(
            self.variables
        )
        # get_logger().debug(f"user_prompt: \n{user_prompt}")

        summary = self.llm.chat_completion(system_prompt, user_prompt)
        curated_summary = json_output_curator(summary)
        # get_logger().debug(f"curated_summary: \n{curated_summary}")

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

        # save to store for future retrieval
        self.store.save(pr_summary, pr_metadata)

        return pr_summary, pr_metadata


if __name__ == "__main__":
    from perfeed.llms.ollama_client import OllamaClient
    from perfeed.llms.openai_client import OpenAIClient

    summarizer = PRSummarizer(
        GithubProvider("Perfeed"),
        llm=OllamaClient(),
        # llm=OpenAIClient(),
        store=FeatherStorage(data_type="pr_summary", overwrite=False, append=True),
    )
    pr_summary, pr_metadata = asyncio.run(summarizer.run("perfeed", 13))
    get_logger().info(f"pr_summary: \n{pr_summary}")
    get_logger().info(f"f pr_metadata: \n{pr_metadata}")
