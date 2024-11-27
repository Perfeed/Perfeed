import pandas as pd
import sqlalchemy as sa
from sqlalchemy import inspect
from pydantic import BaseModel, ValidationError
from perfeed.models.pr_summary import PRSummary, PRSummaryMetadata
from perfeed.data_stores.base import BaseStorage
from typing import Dict
import os
import json


class SQLStorage(BaseStorage):

    def __init__(self, data_type: str, append: bool = True, overwrite: bool = False):
        super().__init__(data_type, append, overwrite)
        self.store_dict = f"../_data/{data_type}"
        self.db_path = os.path.join(self.store_dict, "sqldb_store.sqlite")
        self.data_type = data_type
        # Create a SQLAlchemy engine with the local SQLite database
        self.engine = sa.create_engine(f"sqlite:///{self.db_path}")
        # Ensure the directory for the database file exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def save(self, data: BaseModel, metadata: BaseModel) -> None:
        """Validate, convert, and save the data along with metadata"""
        data_df = self.validate_and_convert(data, metadata)

        # Define SQL write options based on append and overwrite flags
        if_exists_option = (
            "replace" if self.overwrite else "append" if self.append else "fail"
        )

        # Save to SQL table
        data_df.to_sql(
            self.db_path, self.engine, if_exists=if_exists_option, index=False
        )

    def load(self) -> pd.DataFrame:
        """Load data from SQL table"""
        inspector = inspect(self.engine)
        if not inspector.has_table(self.db_path):
            raise FileNotFoundError(
                f"Table '{self.db_path}' does not exist in the database."
            )
        return pd.read_sql_table(self.db_path, self.engine)

    def validate_and_convert(
        self, data: BaseModel, metadata: BaseModel
    ) -> pd.DataFrame:
        data_model = PRSummary
        metadat_model = PRSummaryMetadata
        try:
            data_model.model_validate(data)
            metadat_model.model_validate(metadata)
        except ValidationError as e:
            raise RuntimeError(e)

        # pydantic object to dictionary
        data_dict = data.model_dump()
        metadata_dict = metadata.model_dump()
        data_dict = {k: json.dumps(v) for k, v in data_dict.items()}
        metadata_dict = {k: json.dumps(v) for k, v in metadata_dict.items()}

        return pd.concat(
            [pd.DataFrame([data_dict]), pd.DataFrame([metadata_dict])], axis=1
        )
