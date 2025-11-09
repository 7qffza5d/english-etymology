import os
os.environ["PYTHONUTF8"] = "1"

import pandas as pd
import epitran as ep
from translate import Translator
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

import importlib.resources as pkg_resources
from panphon import featuretable

# Patch featuretable to look up the correct data path
# Why is this necessary? I don't know. PanPhon was being stupid.
if not hasattr(featuretable, "_original_read_bases"):
    featuretable._original_read_bases = featuretable.FeatureTable._read_bases

    def _fixed_read_bases(self, fn, weights):
        if not os.path.exists(fn):
            try:
                fn = pkg_resources.files("panphon.data").joinpath("ipa_all.csv")
            except Exception:
                fn = os.path.join(os.path.dirname(featuretable.__file__), "data", "ipa_all.csv")
        return featuretable._original_read_bases(self, fn, weights)

    featuretable.FeatureTable._read_bases = _fixed_read_bases

df.to_csv("protoresultnoclosest.csv",index=False,encoding="UTF-8")

closest = []
closestWord = []
dst = Distance()

for i in englishWords:
    a = 2147483647
    b = -1
    idx = 0
    for j in df.loc[i]:
        epi = ep.Epitran(languages_ISO_639_3[idx])
        transipa = epi.transliterate(j)
        if dst.feature_edit_distance(i,j) < a:
            a = dst.feature_edit_distance(i,j)
            b = idx
        idx += 1
    closest.append(df.at[i,languages[b]])
    closestWord.append(b)

df.insert(6,"Epitran-PanPhon estimated closest word", closestWord)
df.insert(7,"Epitran-PanPhon estimation",closest)
df.to_csv("protoresult.csv",index=False,encoding="UTF-8")
#df.to_excel("protoresult.xlsx",sheet_name="Sheet1") #honestly i don't know how ts work
