import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def extract_ipa_from_wikipedia(url, lang, outfile):
    print(f"Fetching IPA mappings for {lang}...")
    headers = {"User-Agent": "Mozilla/5.0 (compatible; LinguisticsResearchBot/1.0)"}
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"[Error] Failed to fetch {url}: HTTP {r.status_code}")
        return

    soup = BeautifulSoup(r.text, "html.parser")

    rows = []

    # Find all spans with class="IPA"
    for ipa_span in soup.find_all("span", {"class": "IPA"}):
        ipa = ipa_span.text.strip()

        # Try to find nearby orthography (letter, digraph, etc.)
        # e.g., from the same paragraph or list item
        context = ipa_span.find_parent(["li", "p", "tr"])
        if not context:
            continue

        text = context.get_text(" ", strip=True)
        text = re.sub(r"\(.*?\)", "", text)  # remove notes in parentheses
        text = re.sub(r"\[.*?\]", "", text)
        text = text.strip()

        # Try to extract a Latin/Welsh letter or digraph before the IPA
        # e.g. "c – /k/" or "dd /ð/"
        m = re.search(r"([A-Za-zŵŷâêîôûäëïöüẅẃẁẁŵŷáéíóúàèìòùäëïöüñç]+)\s*[–\-:]?\s*/[^/]+/", text)
        orth = m.group(1) if m else None

        if orth and ipa:
            rows.append((orth, ipa))

    # Deduplicate and save
    if not rows:
        print(f"[Warning] No IPA spans found for {lang}.")
        return

    df = pd.DataFrame(rows, columns=["Orth", "Phon"]).drop_duplicates()
    df.to_csv(outfile, index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} mappings -> {outfile}\n")


latin_url = "https://en.wikipedia.org/wiki/Latin_spelling_and_pronunciation"
welsh_url = "https://en.wikipedia.org/wiki/Welsh_orthography"
greek_url = "https://en.wikipedia.org/wiki/Greek_orthography"

extract_ipa_from_wikipedia(latin_url, "Latin", "latin.csv")
#extract_ipa_from_wikipedia(welsh_url, "Welsh", "welsh.csv")
#extract_ipa_from_wikipedia(greek_url, "Greek", "greek.csv")