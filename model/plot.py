import matplotlib.pyplot as plt
import pandas as pd


df = pd.read_csv('./data.csv')
df_2 = pd.read_csv('./data_filtered.csv')


plt.scatter(df['Temp[C]'], df['Passangers'], color='black', label='Alkuperäinen')
plt.scatter(df_2['Temp[C]'], df_2['Passangers'], color='blue', label='Suodatettu')

plt.savefig('./filter.png')