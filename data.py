from io import BytesIO
import requests
import functools
import numpy as np
import pandas as pd
from pandas.core.frame import DataFrame



class DataHandler: 
    def __init__(self, gss_key) -> None:
        self.df = self.__get_dataframe(gss_key)

    def __get_dataframe(self, gss_key):
        r = requests.get(f'https://docs.google.com/spreadsheet/ccc?key={ gss_key }&output=csv')
        data = r.content
        df = pd.read_csv(BytesIO(data), index_col=0, parse_dates=['seeding_date', 'purchase_date'], dayfirst=True, date_format='%d.%m.%Y')
        return df

    def search_str(self, request: str, case=False) -> DataFrame:
        """ Search string in any column in dataframe """
        mask = functools.reduce(
                np.logical_or,
                [self.df[column].fillna('-').str.contains(request, case=case) for column in self.df.select_dtypes(include=object).columns.tolist()]
            )
        results = self.df.loc[mask]
        return results

