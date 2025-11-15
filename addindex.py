import pandas as pd

englishWords = []

with open("google-10000-english-no-swears.txt","r") as file:
    while len(englishWords) < 250:
        line = file.readline()
        line = line[:-1]
        if len(line) > 1:
            englishWords.append(line)

d = pd.read_csv("protoresultnoclosest.csv")
print(d)
df = pd.DataFrame(data=d)
df.drop(columns='temp',inplace=True)
df.index = englishWords
print(df)
df.to_csv("protoresult.csv")