import pandas as pd

df = pd.read_csv("protoresult.csv")
df.to_excel("result.xlsx")