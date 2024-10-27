from pydantic import BaseModel, ValidationError
from perfeed.models.pr_summary import PRSummary, PRSummaryMetadata
import pandas as pd
import json


def validate_and_convert(data_type: str, data: BaseModel, metadata: BaseModel, is_sqldb: bool=False) -> pd.DataFrame:
    """Validate and convert output data and metadata"""

    if data_type == 'pr_summary':
        data_model = PRSummary
        metadat_model = PRSummaryMetadata
    else:
        raise RuntimeError('data_type not supported.')

    try:
        data_model.model_validate(data)
        metadat_model.model_validate(metadata)
    except ValidationError as e:
        raise RuntimeError(e)
    
    # handle data object before saving
    data_dict = data.model_dump() 
    metadata_dict = metadata.model_dump()
    # todo: double string to handle
    if is_sqldb:
        data_dict = {k: json.dumps(v) for k, v in data_dict.items()}
        metadata_dict = {k: json.dumps(v) for k, v in metadata_dict.items()}
    
    return pd.concat([
        pd.DataFrame.from_dict([data_dict]),
        pd.DataFrame.from_dict([metadata_dict])
    ], axis=1)
    