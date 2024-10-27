import pandas as pd
import sqlalchemy as sa
from sqlalchemy import inspect
from pydantic import BaseModel
from perfeed.data_stores.base import BaseStorage
from perfeed.data_stores.utils import validate_and_convert
from typing import Dict
import os


class SQLStorage(BaseStorage):

    def __init__(self, data_type: str, append: bool = True, overwrite: bool = False):
        super().__init__(data_type, append, overwrite)
        self.store_dict = f'_data/{data_type}'
        self.db_path = os.path.join(self.store_dict, 'sqldb_store.sqlite')
        self.data_type = data_type
        # Create a SQLAlchemy engine with the local SQLite database
        self.engine = sa.create_engine(f"sqlite:///{self.db_path}")
        # Ensure the directory for the database file exists
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)

    def save(self, data: BaseModel, metadata: BaseModel) -> None:
        """Validate, convert, and save the data along with metadata"""
        data = validate_and_convert(self.data_type, data, metadata, is_sqldb=True)
        
        # Define SQL write options based on append and overwrite flags
        if_exists_option = 'replace' if self.overwrite else 'append' if self.append else 'fail'
        
        # Save to SQL table
        data.to_sql(self.db_path, self.engine, if_exists=if_exists_option, index=False)

    def load(self) -> pd.DataFrame:
        """Load data from SQL table"""
        inspector = inspect(self.engine)
        if not inspector.has_table(self.db_path):
            raise FileNotFoundError(f"Table '{self.table_name}' does not exist in the database.")
        return pd.read_sql_table(self.db_path, self.engine)
