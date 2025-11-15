import os
os.environ["PYTHONUTF8"] = "1"

import pandas as pd
from translate import Translator

englishWords = []

with open("google-10000-english-no-swears.txt","r") as file:
    while len(englishWords) < 250:
        line = file.readline()
        line = line[:-1]
        if len(line) > 1:
            englishWords.append(line)

#latin, dutch, norwegian, french

latinWords = []
translator = Translator(to_lang="la",from_lang="en")
for i in englishWords:
    str = translator.translate(i)
    str = str.lower()
    if(str.find(',') != -1):
        str = str[:str.find(',')]
    if(str.find('/') != -1):
        str = str[:str.find('/')]
    latinWords.append(str)

dutchWords = []
translator = Translator(to_lang="nl",from_lang="en")
for i in englishWords:
    str = translator.translate(i)
    str = str.lower()
    if(str.find(',') != -1):
        str = str[:str.find(',')]
    if(str.find('/') != -1):
        str = str[:str.find('/')]
    dutchWords.append(str)

norseWords = []
translator = Translator(to_lang="no",from_lang="en")
for i in englishWords:
    str = translator.translate(i)
    str = str.lower()
    if(str.find(',') != -1):
        str = str[:str.find(',')]
    if(str.find('/') != -1):
        str = str[:str.find('/')]
    norseWords.append(str)

frenchWords = []
translator = Translator(to_lang="fr",from_lang="en")
for i in englishWords:
    str = translator.translate(i)
    str = str.lower()
    if(str.find(',') != -1):
        str = str[:str.find(',')]
    if(str.find('/') != -1):
        str = str[:str.find('/')]
    frenchWords.append(str)

d = {"Latin": latinWords, "Old English": dutchWords, "Old Norse": norseWords,
      "Middle French": frenchWords}
languages = ["Latin", "Old English", "Old Norse", "Middle French"]
df = pd.DataFrame(data=d)

df.to_csv("protoresultnoclosest.csv",encoding="UTF-8")

