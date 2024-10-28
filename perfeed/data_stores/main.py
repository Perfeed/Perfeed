import asyncio
from perfeed.data_stores.storage_feather import FeatherStorage
from perfeed.data_stores.storage_sqldb import SQLStorage
from perfeed.tools.pr_summarizer import PRSummarizer
from perfeed.git_providers.github import GithubProvider
from perfeed.llms.ollama_client import OllamaClient


# todo: once Henry's local test pipeline is merged, this will be moved

if __name__ == "__main__":
    summarizer = PRSummarizer(GithubProvider("Perfeed"), llm=OllamaClient("llama3.2"))
    pr_summary, metadata =  asyncio.run(summarizer.run("perfeed", 5))
    
    # test feather
    fs = FeatherStorage(
        data_type="pr_summary",
        overwrite=True, 
        append=False
    )
    fs.save(data=pr_summary, metadata=metadata)
    fs.load()

    # test sql
    ss = SQLStorage(
        data_type="pr_summary",
        overwrite=True, 
        append=False
    )
    ss.save(data=pr_summary, metadata=metadata)
    ss.load()

