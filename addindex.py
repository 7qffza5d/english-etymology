import pandas as pd

englishWords = []

with open("google-10000-english-no-swears.txt","r") as file:
    while len(englishWords) < 250:
        line = file.readline()
        if len(line) > 1 or line == 'a' or line == 'i':
            englishWords.append(line)

d = pd.read_csv("protoresultnoclosest.csv")
print(d)
df = pd.DataFrame(d[["Brythonic", "Latin", "Old English", "Old Norse", "Middle French", "Greek"]], index=englishWords)
print(df)
df.to_csv("protoresult.csv")