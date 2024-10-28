from abc import ABC, abstractmethod
from pydantic import BaseModel
from typing import Dict
import pandas as pd
from perfeed.models.pr_summary import PRSummary


class UnsupportedFormatError(Exception):
    """Exception raised for unsupported storage formats."""
    pass


class BaseStorage(ABC):
    """Abstract base class for storage handlers."""
    
    def __init__(self, data_type: str, append: bool = True, overwrite: bool = False):
        self.data_type = data_type
        self.overwrite = overwrite
        self.append = append
        self._validate_options()

    def _validate_options(self):
        if self.overwrite and self.append:
            raise ValueError("Cannot set both overwrite and append to True simultaneously.")

    @abstractmethod
    def save(self, data: PRSummary, metadata: Dict) -> None:
        pass
    
    @abstractmethod
    def load(self) -> pd.DataFrame:
        pass
    
    @abstractmethod
    def validate_and_convert(data: BaseModel, metadata: BaseModel) -> pd.DataFrame:
        pass
