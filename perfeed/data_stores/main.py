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

    def save(self, data: BaseModel, metadata: Dict) -> None:
        self.storage.save(data=data, metadata=metadata)

    def load(self) -> pd.DataFrame:
        return self.storage.load()

    @classmethod
    def from_format(cls, store_type: str, **kwargs) -> BaseStorage:
        """initialize store type."""

        if store_type == "feather":
            data_type = kwargs.get("data_type")
            overwrite = kwargs.get("overwrite", True)
            append = kwargs.get("append", False)
            return cls(FeatherStorage(data_type=data_type, overwrite=overwrite, append=append))
        
        elif store_type == "sql":
            db_url = kwargs.get("db_url")
            table_name = kwargs.get("table_name")
            overwrite = kwargs.get("overwrite", True)
            append = kwargs.get("append", False)
            if not db_url or not table_name:
                raise ValueError("Both db_url and table_name are required for SQL storage.")
            return cls(SQLStorage(db_url=db_url, table_name=table_name, overwrite=overwrite, append=append))
        else:
            raise UnsupportedFormatError(f"{store_type} is not supported.")
