from pydantic import BaseModel, ValidationError
from perfeed.models.pr_summary import PRSummary
import pandas as pd


def validate_and_convert(data_type: str, data: BaseModel) -> pd.DataFrame:
    if data_type == 'pr_summary':
        model = PRSummary
    else:
        raise RuntimeError('data_type not supported.')

    try:
        model.model_validate(data)
    except ValidationError as e:
        raise RuntimeError(e)
    
    return pd.DataFrame.from_dict([data.model_dump()])
    