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
        df = pd.read_csv(
            BytesIO(data), 
            parse_dates=['seeding_date', 'purchase_date'], 
            dayfirst=True, 
            date_format='%d.%m.%Y', 
            dtype={'uid': str}
        )
        return df

    def __search(self, df: DataFrame, request: str, case=False) -> DataFrame:
        """ Search string in any column in dataframe """
        mask = functools.reduce(
                np.logical_or,
                [df[column].fillna('-').str.contains(request, case=case) for column in df.select_dtypes(include=object).columns.tolist()]
            )
        results = df.loc[mask]
        return results
    
    def search(self, request: str) -> DataFrame:
        """ Multiple word search"""
        requests = request.split()
        print(requests)
        df_filtered = self.df
        for r in requests:
            print(r, len(df_filtered))
            df_filtered = self.__search(df_filtered, r)
        return df_filtered

    def get_plant_by_uid(self, uid: str) -> DataFrame:
        """ Returns plant (as DataFrame) by uid or None """
        return self.df.loc[self.df.uid == uid]        
    
    
