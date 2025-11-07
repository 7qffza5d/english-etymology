import pandas as pd
import unicodedata
import re

def clean(inp, out):
    df = pd.read_csv(inp, encoding="utf-8-sig")
    df.columns = [c.strip().replace("\ufeff", "") for c in df.columns]
    print("Original:", len(df))

    df["Orth"] = df["Orth"].apply(lambda x: unicodedata.normalize("NFC", str(x).strip().lower()))
    df["Phon"] = df["Phon"].apply(lambda x: unicodedata.normalize("NFC", str(x).strip()))

    # Relax filters
    # df = df[~df["Orth"].isin(drop_words)]  # try disabling temporarily
    df = df[df["Orth"].str.len() <= 6]
    print("After length filter:", len(df))

    # Relax regex
    #pattern = re.compile(r"^[a-zA-Zɨɬθðʃχəɔɛɑːuːiːʊɨ̞ˈ̯\.~ ,]+$")
    #df = df[df["Phon"].apply(lambda x: bool(pattern.match(x)))]
    #print("After phon filter:", len(df))

    df = df.drop_duplicates(subset="Orth", keep="first")
    print("After dedup:", len(df))

    df = df.assign(length=df["Orth"].str.len()).sort_values(by="length", ascending=False).drop(columns="length")

    df.to_csv(out, index=False, encoding="utf-8")
    print(f"Cleaned file saved as {out}")

#clean("welsh.csv", "cym-Latn.csv")
clean("latin.csv","lat-Latn.csv")
