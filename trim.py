import pandas as pd
import re

df = pd.read_csv("cym-Latn.csv", encoding="utf-8-sig")

clean_rows = []
for _, row in df.iterrows():
    orth = row["Orth"].strip().lower()
    phon_raw = str(row["Phon"])

    # remove slashes and quotes
    phon_raw = phon_raw.replace("/", "")
    phon_raw = phon_raw.replace('"', "")
    phon_raw = phon_raw.strip()

    # handle variant separators (~, commas)
    variants = re.split(r"[~,]", phon_raw)

    for v in variants:
        v = v.strip()
        if v:
            clean_rows.append((orth, v))

clean_df = pd.DataFrame(clean_rows, columns=["Orth", "Phon"])
clean_df = clean_df.drop_duplicates().reset_index(drop=True)

clean_df.to_csv("cym-Latn.csv", index=False, encoding="utf-8")
print("Cleaned mapping saved to cym-Latn.csv")
