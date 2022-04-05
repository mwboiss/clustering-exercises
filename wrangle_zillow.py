import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns

import os
import env

def acquire_zillow(use_cache=True):
    
    filename = ('zillow.csv')
    if os.path.exists(filename) and use_cache:
        print('Using CSV')
        return pd.read_csv(filename)
    
    
    print('Acquiring from Database')
    url = env.get_db_url('zillow')

    zillow = pd.read_sql('''
    SELECT *
    FROM properties_2017
    JOIN (SELECT parcelid as pid, MAX(transactiondate) as maxdate FROM predictions_2017 GROUP BY parcelid) as last_date
    ON last_date.pid = parcelid
    LEFT JOIN (SELECT parcelid as pid, transactiondate as maxdate, logerror FROM predictions_2017) as log
    ON last_date.pid = log.pid AND last_date.maxdate = log.maxdate
    LEFT JOIN propertylandusetype
    USING(propertylandusetypeid)
    LEFT JOIN storytype
    USING(storytypeid)
    LEFT JOIN typeconstructiontype
    USING(typeconstructiontypeid)
    LEFT JOIN airconditioningtype
    USING(airconditioningtypeid)
    LEFT JOIN architecturalstyletype
    USING(architecturalstyletypeid)
    LEFT JOIN buildingclasstype
    USING(buildingclasstypeid)
    LEFT JOIN heatingorsystemtype
    USING(heatingorsystemtypeid)
    ''',url)

    print('Saving to CSV')
    zillow.to_csv('zillow.csv',index=False)
    return zillow

def initial_look(df):
    print(f'Shape:\n\n{df.shape}\n\n')
    print(f'Describe:\n\n{df.describe(include="all")}\n\n')
    print(f'Info:\n\n{df.info()}\n\n')
    print(f'Histograms:\n\n{df.hist(figsize=(40,20), bins =20), plt.show()}')
    
def missing_rows(df):
    return pd.concat([
           df.isna().sum().rename('count'),
           df.isna().mean().rename('percent')
           ], axis=1)

def missing_columns(df):
    col_missing = pd.concat([
    df.isna().sum(axis=1).rename('num_cols_missing'),
    df.isna().mean(axis=1).rename('pct_cols_missing'),
    ], axis=1).value_counts().sort_index()
    col_missing = pd.DataFrame(col_missing)
    col_missing.rename(columns={0:'num_rows'},inplace=True)
    return col_missing.reset_index()

def handle_missing_values(df,required_col,required_row):
    required_row = round(df.shape[1] * required_row)
    required_col = round(df.shape[0] * required_col)
    df.dropna(axis=0, thresh=required_row, inplace=True)
    df.dropna(axis=1, thresh=required_col, inplace=True)
    return df

def wrangle_zillow(df):
    df.drop(columns=['id','pid','maxdate'],inplace=True)
    df.dropna(subset=['latitude','longitude'],inplace=True)
    df = df[df['propertylandusetypeid'].isin([260,261,263,264,266,267,269])]
    df = df[~df['unitcnt'].isin([2.0,3.0,4.0,6.0])]
    handle_missing_values(df,0.5,0.5)
    df.dropna(inplace=True)
    return df