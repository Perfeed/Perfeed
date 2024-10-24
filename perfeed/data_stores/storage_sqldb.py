import pandas as pd
import sqlalchemy as sa
from pydantic import BaseModel

from perfeed.data_stores.base import BaseStorage
from perfeed.data_stores.utils import validate_and_convert

class SQLStorage(BaseStorage):

    def __init__(self, db_url: str, table_name: str, append: bool = True, overwrite: bool = False):
        super().__init__(table_name, append, overwrite)
        self.engine = sa.create_engine(db_url)

    def save(self, data: BaseModel) -> None:
        data = validate_and_convert(self.data_type, data)
        if_exists_option = 'replace' if self.overwrite else 'append' if self.append else 'fail'
        data.to_sql(self.path, self.engine, if_exists=if_exists_option, index=False)

    def load(self) -> pd.DataFrame:
        return pd.read_sql_table(self.path, self.engine)
    