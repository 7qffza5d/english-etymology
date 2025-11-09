import os
os.environ["PYTHONUTF8"] = "1"

import pandas as pd
import epitran as ep
from translation import Translator
from panphon.distance import Distance

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

englishWords = []

with open("google-10000-english-no-swears.txt","r") as file:
    while len(englishWords) < 250:
        line = file.readline()
        if len(line) > 1 or line == 'a' or line == 'i':
            englishWords.append(line)

closest = []
closestWord = []
dst = Distance()

df = pd.read_csv("protoresultnoclosest.csv")
df.index = englishWords
languages = ["Brythonic", "Latin", "Old English", "Old Norse", "Middle French", "Greek"]
languages_ISO_639_3 = ["cym-Latn","lat-Latn","deu-Latn","nno-Latn","fra-Latn","ell-Grek"]

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
df.to_csv("protoresult.csv",encoding="UTF-8")
#df.to_excel("protoresult.xlsx",sheet_name="Sheet1") #honestly i don't know how ts work
