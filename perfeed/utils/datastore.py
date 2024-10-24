from dataclasses import dataclass
from functools import partial
import pandas as pd
import sqlite3
import os
from perfeed.models.pr_summary import PRSummary


@dataclass
class OutputStore:
    """
    OutputStore has options to save outputs to feather or sqlite database.
    saver: take one output and append to existing ones.
    loader: load all saved output 
    """

    output_type: str

    def _init__(self, db_type: str = 'feather'):
        if db_type == 'feather':
            self.creater = partial(self.create_feather)
            self.saver = partial(self.save_feather)
            self.loader = partial(self.load_feather)
        else:
            self.creater = partial(self.create_db)
            self.saver = partial(self.save_db)
            self.loader = partial(self.load_db)
        self.file_name = f'{self.output_type}_{db_type}'
        self.data_dict = f'~/perfeed/_data/{db_type}'
        if not os.path.exists(self.data_dict):
            os.makedirs(self.data_dict)
        self.file_path = os.path.join(self.data_dict, self.file_name)
        if not os.path.exists(self.file_path):
            self.creater()

        self.output = self.loader()    

    def create_feather(self):
        pd.DataFrame().to_feather(self.file_path)
    
    def create_db(self):
        self._db_save(pd.DataFrame())

    def load_feather(self):
        return pd.read_feather(self.file_path)
        
    def load_db(self):
        conn = sqlite3.connect(self.file_path)
        query = f"SELECT * FROM {self.file_name}"
        df = pd.read_sql(query, conn)
        conn.close()
        return df
        
    def save_feather(self, pr_summary_object: PRSummary):
        df = pd.DataFrame(
            {
                'owner': PRSummary.owner,
                'repo': PRSummary.repo,
                'model': PRSummary.model,
                'author': PRSummary.author,
                'pr_number': PRSummary.pr_number,
                'output': PRSummary.output,
            }
        )
        pd.concat([self.output, df]).to_feather(self.file_path)
        print(f"Save to exsiting")
    

    def _db_save(self, df):
        conn = sqlite3.connect(self.file_name)
        df.to_sql(self.table_name, conn, if_exists='replace', index=False)
        conn.close()

    def save_db(
        self,
            owner: str,
            repo: str,
            model: str,    
            author: str,
            pr_number: str,
            output: str
    ):
        df = pd.DataFrame(
            {
                'owner': owner,
                'repo': repo,
                'model': model,
                'author': author,
                'pr_number': pr_number,
                'output': output,
            }
        )
        self._db_save(pd.concat([self.output, df]))
        
