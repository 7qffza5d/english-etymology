import os
os.environ["PYTHONUTF8"] = "1"

import pandas as pd
import epitran as ep
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
        line = line[:-1]
        if len(line) > 1:
            englishWords.append(line)

closest = []
closestWord = []
dst = Distance()

df = pd.read_csv("protoresultnoclosest.csv",sep=r'\s*,\s*',engine='python')
df.index = englishWords
languages = ["Latin", "Old English", "Old Norse", "Middle French"]
languages_ISO_639_3 = ["lat-Latn","nld-Latn","nno-Latn","fra-Latn"]

blacklist = ['','-']

for i in englishWords:
    a = 2147483647
    b = -1
    idx = 0
    for j in languages:
        currWord = df.at[i, j]
        if currWord in blacklist or not isinstance(currWord,str):
            idx += 1
            continue
        if idx > 5:
            break
        epi = ep.Epitran(languages_ISO_639_3[idx])
        transipa = epi.transliterate(currWord)
        if dst.feature_edit_distance(i,currWord) < a:
            a = dst.feature_edit_distance(i,currWord)
            b = idx
        idx += 1
    closest.append(df.at[i,languages[b]])
    closestWord.append(languages[b])

df.insert(5,"Epitran-PanPhon estimated closest word", closestWord)
df.insert(6,"Epitran-PanPhon estimation",closest)

df.to_csv("protoresult.csv",encoding="UTF-8")
