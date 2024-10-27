import pandas as pd
import os
from pydantic import BaseModel
from perfeed.data_stores.base import BaseStorage
from perfeed.data_stores.utils import validate_and_convert
from typing import Dict

class FeatherStorage(BaseStorage):

    def __init__(self, data_type: str, append: bool = True, overwrite: bool = False):
        super().__init__(data_type, append, overwrite)

        # initialize the storage path
        self.store_dict = f'_data/{data_type}'
        os.makedirs(self.store_dict, exist_ok=True)
        self.path = os.path.join(self.store_dict, f'feather_store')
        if not os.path.exists(self.path):
            pd.DataFrame().to_feather(self.path)

    def save(self, data: BaseModel, metadata: BaseModel) -> None:
        """validate, convert, and save the data"""
        
        data = validate_and_convert(self.data_type, data, metadata)        
        if os.path.exists(self.path):
            if self.append:
                existing_data = pd.read_feather(self.path)
                data = pd.concat([existing_data, data], ignore_index=True)
            elif not self.overwrite:
                raise FileExistsError(f"{self.path} already exists. Set overwrite=True to overwrite.")
        data.to_feather(self.path)

    def load(self) -> pd.DataFrame:
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"{self.path} does not exist.")
        return pd.read_feather(self.path)
    