import pandas as pd
import epitran as ep
from translate import Translator
import panphon as pp

englishWords = []

with open("google-10000-english-no-swears.txt","r") as file:
    while len(englishWords) < 5:
        line = file.readline()
        if len(line) > 1 or line == 'a' or line == 'i':
            englishWords.append(line)

#welsh, latin, german, norwegian, french, greek 

welshWords = []
translator = Translator(to_lang="cy") #this is the ISO 639-1 code
for i in englishWords:
    welshWords.append(translator.translate(i))

latinWords = []
translator = Translator(to_lang="la")
for i in englishWords:
    latinWords.append(translator.translate(i))

germanWords = []
translator = Translator(to_lang="de")
for i in englishWords:
    germanWords.append(translator.translate(i))

norseWords = []
translator = Translator(to_lang="no")
for i in englishWords:
    norseWords.append(translator.translate(i))

frenchWords = []
translator = Translator(to_lang="fr")
for i in englishWords:
    frenchWords.append(translator.translate(i))

greekWords = []
translator = Translator(to_lang="el")
for i in englishWords:
    greekWords.append(translator.translate(i))

d = {"Brythonic": welshWords, "Latin": latinWords, "Old English": germanWords, "Old Norse": norseWords,
      "Middle French": frenchWords, "Greek": greekWords}
languages = ["Brythonic", "Latin", "Old English", "Old Norse", "Middle French", "Greek"]
languages_ISO_639_3 = ["cym-Latn.csv","lat-Latn.csv","deu-Latn.csv","nor-Latn.csv","fra-Latn.csv"]
df = pd.DataFrame(data=d, index=englishWords)

