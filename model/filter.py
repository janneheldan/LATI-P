import matplotlib.pyplot as plt
import pandas as pd


df = pd.read_csv('./data.csv')

arr = df.groupby(['Month']).agg({'Passangers': ['mean', 'std', 'count']})


for i in df.index:
    month = df.loc[i]['Month']
    average = arr['Passangers']['mean'][month]
    deviation = arr['Passangers']['std'][month]
    if df.loc[i]['Passangers'] > average + 2*deviation:
        df.drop(i, inplace=True)
    elif df.loc[i]['Passangers'] < average - 2*deviation:
        df.drop(i, inplace=True)

df.to_csv('./data_filtered.csv', index=False)









