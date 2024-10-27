from typing import Any
from pydantic import BaseModel
from perfeed.data_stores.base import (
    BaseStorage, 
    UnsupportedFormatError
)
from perfeed.data_stores.storage_feather import FeatherStorage
from perfeed.data_stores.storage_sqldb import SQLStorage
from perfeed.models.pr_summary import PRSummary
import pandas as pd
from typing import Dict


class DataStore:
    """Storage frontend handling multiple storage backends."""
    
    def __init__(self, storage: BaseStorage=FeatherStorage) -> None:
        self.storage = storage

    def save(self, data: BaseModel, metadata: BaseModel) -> None:
        self.storage.save(data=data, metadata=metadata)

    def load(self) -> pd.DataFrame:
        return self.storage.load()

    @classmethod
    def from_format(cls, store_type: str, **kwargs) -> BaseStorage:
        """initialize store type."""

        data_type = kwargs.get("data_type")
        overwrite = kwargs.get("overwrite", True)
        append = kwargs.get("append", False)

        if store_type == "feather":
            return cls(FeatherStorage(data_type=data_type, overwrite=overwrite, append=append))
        
        elif store_type == "sql":            
            return cls(SQLStorage(data_type=data_type, overwrite=overwrite, append=append))
        else:
            raise UnsupportedFormatError(f"{store_type} is not supported.")


if __name__ == "__main__":
    from perfeed.tools.pr_summarizer import PRSummarizer
    from perfeed.git_providers.github import GithubProvider
    from perfeed.llms.ollama_client import OllamaClient

    summarizer = PRSummarizer(GithubProvider("Perfeed"), llm=OllamaClient("llama3.2"))
    pr_summary, metadata = summarizer.run("perfeed", 5)

    # save and load
    ds = DataStore.from_format(    
        # store_type="feather",
        store_type="sql",
        data_type="pr_summary",
        overwrite=True, 
        append=False
    )
    ds.save(data=pr_summary, metadata=metadata)
    ds.load()

    # load only
    ds2 = DataStore.from_format(    
        # store_type="feather",
        store_type="sql",
        data_type="pr_summary",
        overwrite=True, 
        append=False
    )
    ds2.load()
