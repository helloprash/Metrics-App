import pandas as pd


df = pd.read_excel('dataFrame.xlsx')

print(df['CF number'].to_list())

print(df)