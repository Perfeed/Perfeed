import pandas as pd
import os
from pydantic import BaseModel, ValidationError
from perfeed.data_stores.base import BaseStorage
from perfeed.models.pr_summary import PRSummary, PRSummaryMetadata
from typing import Dict
import json


class FeatherStorage(BaseStorage):

    def __init__(self, data_type: str, append: bool = True, overwrite: bool = False):
        super().__init__(data_type, append, overwrite)

        # initialize the storage path
        self.store_dict = f"../_data/{data_type}"
        os.makedirs(self.store_dict, exist_ok=True)
        self.path = os.path.join(self.store_dict, f"feather_store")
        if not os.path.exists(self.path):
            pd.DataFrame().to_feather(self.path)

    def save(self, data: BaseModel, metadata: BaseModel) -> None:
        """validate, convert, and save the data"""

        data_df = self.validate_and_convert(data, metadata)
        if os.path.exists(self.path):
            if self.append:
                existing_data_df = pd.read_feather(self.path)
                data_df = pd.concat([existing_data_df, data_df], ignore_index=True)
            elif not self.overwrite:
                raise FileExistsError(
                    f"{self.path} already exists. Set overwrite=True to overwrite."
                )
        data_df.to_feather(self.path)

    def load(self) -> pd.DataFrame:
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"{self.path} does not exist.")
        return pd.read_feather(self.path)

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

        return pd.concat(
            [pd.DataFrame([data_dict]), pd.DataFrame([metadata_dict])], axis=1
        )
