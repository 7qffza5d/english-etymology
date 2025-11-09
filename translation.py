import os
os.environ["PYTHONUTF8"] = "1"

import pandas as pd
import epitran as ep
from translation import Translator
from panphon.distance import Distance

englishWords = []

with open("google-10000-english-no-swears.txt","r") as file:
    while len(englishWords) < 250:
        line = file.readline()
        if len(line) > 1 or line == 'a' or line == 'i':
            englishWords.append(line)

#welsh, latin, german, norwegian, french, greek 

welshWords = []
translator = Translator(to_lang="cy",from_lang="en") #this is the ISO 639-1 code
for i in englishWords:
    welshWords.append(translator.translate(i))

latinWords = []
translator = Translator(to_lang="la",from_lang="en")
for i in englishWords:
    latinWords.append(translator.translate(i))

germanWords = []
translator = Translator(to_lang="de",from_lang="en")
for i in englishWords:
    germanWords.append(translator.translate(i))

norseWords = []
translator = Translator(to_lang="no",from_lang="en")
for i in englishWords:
    norseWords.append(translator.translate(i))

frenchWords = []
translator = Translator(to_lang="fr",from_lang="en")
for i in englishWords:
    frenchWords.append(translator.translate(i))

greekWords = []
translator = Translator(to_lang="el",from_lang="en")
for i in englishWords:
    greekWords.append(translator.translate(i))

d = {"Brythonic": welshWords, "Latin": latinWords, "Old English": germanWords, "Old Norse": norseWords,
      "Middle French": frenchWords, "Greek": greekWords}
languages = ["Brythonic", "Latin", "Old English", "Old Norse", "Middle French", "Greek"]
languages_ISO_639_3 = ["cym-Latn","lat-Latn","deu-Latn","nno-Latn","fra-Latn","ell-Grek"]
df = pd.DataFrame(data=d, index=englishWords)

df.to_csv("protoresultnoclosest.csv",index=False,encoding="UTF-8")

