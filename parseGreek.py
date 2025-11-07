#!/usr/bin/env python3
# extract_greek_orthography.py
# Usage: python extract_greek_orthography.py
# Edit PAGE_URL below to point to the particular Wikipedia page you want to parse.

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import unicodedata
import sys
import os

# ---------- CONFIG ----------
# Put the Wikipedia page you want to parse here (Modern Greek orthography/phonology pages are good)
PAGE_URL = "https://en.wikipedia.org/wiki/Greek_orthography"
OUTFILE = "ell-Grek.csv"   # recommended name: ISO639-3-script (ell for Modern Greek) but change as you like
USER_AGENT = "Mozilla/5.0 (compatible; LinguisticsScraper/1.0; +https://example.org/)"
# Max orthographic length to keep (to avoid keeping full example words accidentally)
MAX_ORTH_LEN = 6
# ----------------------------

def flatten_columns(columns):
    """Flatten MultiIndex into single header strings."""
    if isinstance(columns, pd.MultiIndex):
        return [" ".join([str(x) for x in tup if str(x) != "nan"]).strip() for tup in columns.values]
    else:
        return [str(c) for c in columns]

def clean_orth(s):
    s = str(s).strip()
    s = unicodedata.normalize("NFC", s)
    return s

def clean_phon(s):
    s = str(s).strip()
    s = s.replace('"', "").replace("'", "")
    s = s.replace("–", "-")  # normalize dash
    # remove / slashes commonly used around IPA
    s = s.replace("/", "")
    s = unicodedata.normalize("NFC", s)
    s = s.strip()
    return s

def split_variants(phon_raw):
    # split on commas, semicolons, tildes (~), " or ", " / " and on " or " in English
    parts = re.split(r'\s*(?:,|;|~| or |/|\u2013|\u2014|\|)\s*', phon_raw)
    # additional splitting where multiple entries are separated by whitespace + comma inside quotes
    cleaned = []
    for p in parts:
        p = p.strip()
        if not p:
            continue
        # remove enclosing parentheses
        p = re.sub(r'^\(+', '', p)
        p = re.sub(r'\)+$', '', p)
        if p:
            cleaned.append(p)
    return cleaned

def find_table_mappings(soup):
    """Look for tables that contain a letter/grapheme column and an IPA/pronunciation column."""
    rows = []
    tables = soup.find_all("table")
    for t in tables:
        try:
            df_list = pd.read_html(str(t))
        except Exception:
            continue
        if not df_list:
            continue
        for df in df_list:
            # flatten multiindex headers
            df.columns = flatten_columns(df.columns)
            cols_lower = [str(c).lower() for c in df.columns]

            # heuristics to find index of orthography and ipa columns
            orth_idx = None
            ipa_idx = None
            for i, h in enumerate(cols_lower):
                # common English headers (letter, grapheme, orthography)
                if re.search(r'\b(letter|grapheme|orthograph|orthography|symbol|character)\b', h):
                    orth_idx = i
                # Greek headers heuristics: "γράμμα" (gramma), "γράφημα", "γράμ" etc
                if re.search(r'γράμμ|γράφημα|γράμμα|γράφ', h):
                    orth_idx = i if orth_idx is None else orth_idx
                # IPA/pronunciation columns
                if "ipa" in h or re.search(r'pronounc|pronunc|pronunci|transcription|sound', h):
                    ipa_idx = i

            # fallback: try to find any column that contains "/" or "ɡ ɪ ʃ" characters often in IPA cells
            if ipa_idx is None:
                for i, col in enumerate(df.columns):
                    sample_vals = df[col].astype(str).head(10).str.cat(sep=" ")
                    if re.search(r'[ɡɣθðʃʒŋɲɸχɬɾˈˌəɔɛɑɪɯɨʊʉʎʝʰː]', sample_vals):
                        ipa_idx = i
                        break

            if orth_idx is None or ipa_idx is None:
                continue

            # extract row pairs
            for _, row in df.iterrows():
                orth = str(row[df.columns[orth_idx]]).strip()
                ipa = str(row[df.columns[ipa_idx]]).strip()
                if orth and ipa and orth.lower() not in ["nan", "–", "-", "—"]:
                    rows.append((clean_orth(orth), clean_phon(ipa)))
    return rows

def find_span_ipa_mappings(soup):
    """Find span class='IPA' and try to locate orthography nearby (list items, table cells, paragraphs)."""
    rows = []
    for ipa_span in soup.find_all("span", class_="IPA"):
        ipa_text = ipa_span.get_text(" ", strip=True)
        if not ipa_text:
            continue
        # search containing element (li, tr, p, dd)
        parent = ipa_span.find_parent(["li", "tr", "p", "dd", "dt", "td"])
        if parent:
            text = parent.get_text(" ", strip=True)
            # remove bracketed notes
            text = re.sub(r'\(.*?\)', '', text)
            text = re.sub(r'\[.*?\]', '', text)
            # Look for patterns like "Χ — /x/" or "ch – /x/" or "Letter: /ipa/"
            # Try a few regexes to capture the orth before the IPA
            # 1) letter (maybe with accent) followed by dash or colon then IPA
            m = re.search(r'([A-Za-z\u0370-\u03FF\u1F00-\u1FFF]{1,6})\s*[–—\-:]\s*\/?'+re.escape(ipa_text), text)
            if m:
                orth = m.group(1)
                rows.append((clean_orth(orth), clean_phon(ipa_text)))
                continue
            # 2) look for orth directly to the left up to 8 chars (useful for 'letter — /ipa/' or 'α /a/')
            m2 = re.search(r'([A-Za-z\u0370-\u03FF\u1F00-\u1FFF]{1,6})\s+\/?' + re.escape(ipa_text), text)
            if m2:
                orth = m2.group(1)
                rows.append((clean_orth(orth), clean_phon(ipa_text)))
                continue
            # 3) if the parent is a table row, try pairing cells left-of-right
            if parent.name == "tr":
                cells = parent.find_all(["td","th"])
                # try to find which cell contains this span and pair with a left neighbour
                for idx, c in enumerate(cells):
                    if ipa_span in c.descendants:
                        if idx > 0:
                            orth = cells[idx-1].get_text(" ", strip=True)
                            rows.append((clean_orth(orth), clean_phon(ipa_text)))
                        break
            # 4) fallback: attempt to guess orth as first token in the parent text
            tokens = re.split(r'\s+|-|,|—|–|:|;', text)
            if tokens:
                first = tokens[0].strip()
                if len(first)>0 and len(first) <= MAX_ORTH_LEN:
                    rows.append((clean_orth(first), clean_phon(ipa_text)))
    return rows

def find_inline_mappings_by_regex(soup):
    """Search for common inline forms like 'α — /a/' in paragraphs and list items."""
    rows = []
    texts = []
    for tag in soup.find_all(['p','li','dd','dt']):
        texts.append(tag.get_text(" ", strip=True))
    bigtext = "\n".join(texts)
    # patterns like "α — /a/" or "alpha – /ˈal.fa/" or "c — /k/"
    for m in re.finditer(r'([A-Za-z\u0370-\u03FF\u1F00-\u1FFF]{1,6})\s*(?:—|–|-|:)\s*\/([^\/]+)\/', bigtext):
        orth = m.group(1)
        ipa = m.group(2)
        rows.append((clean_orth(orth), clean_phon(ipa)))
    # patterns like "Letter: α /a/"
    for m in re.finditer(r'([A-Za-z\u0370-\u03FF\u1F00-\u1FFF]{1,6})\s*\/([^\/]+)\/', bigtext):
        orth = m.group(1)
        ipa = m.group(2)
        rows.append((clean_orth(orth), clean_phon(ipa)))
    return rows

def postprocess_rows(rows):
    # normalize and split variant pronunciations
    clean = []
    for orth, phon in rows:
        orth = orth.strip()
        phon = phon.strip()
        if not orth or orth.lower() in ["nan","none","–","-","—"]:
            continue
        # remove trailing examples like "eg." or "see"
        # split variant groups
        variants = split_variants(phon)
        for v in variants:
            v = v.strip()
            # drop obviously English words accidentally captured
            if re.match(r'^[A-Za-z\s\-]{4,}$', orth) and not re.search(r'[\u0370-\u03FF]', orth):
                # if orth has only Latin letters and is long (>=4), it's likely a word, not a grapheme
                continue
            if len(orth) > MAX_ORTH_LEN:
                # skip very long orthographic strings (likely example words)
                continue
            # keep
            clean.append((orth, v))
    # dedupe by keeping first occurrence
    seen = set()
    final = []
    for o,p in clean:
        key = (o,p)
        if key not in seen:
            seen.add(key)
            final.append((o,p))
    return final

def main():
    print("Fetching:", PAGE_URL)
    headers = {"User-Agent": USER_AGENT}
    r = requests.get(PAGE_URL, headers=headers, timeout=30)
    if r.status_code != 200:
        print("Failed to fetch page:", r.status_code)
        sys.exit(1)
    soup = BeautifulSoup(r.text, "html.parser")

    rows = []
    # 1) table-based extraction
    try:
        trows = find_table_mappings(soup)
        print(f"Found {len(trows)} candidate rows from tables")
        rows.extend(trows)
    except Exception as e:
        print("Table extraction error:", e)

    # 2) span.ipa extraction
    try:
        srows = find_span_ipa_mappings(soup)
        print(f"Found {len(srows)} candidate rows from IPA spans")
        rows.extend(srows)
    except Exception as e:
        print("Span IPA extraction error:", e)

    # 3) inline regex extraction
    try:
        irows = find_inline_mappings_by_regex(soup)
        print(f"Found {len(irows)} candidate rows from inline regex")
        rows.extend(irows)
    except Exception as e:
        print("Inline regex extraction error:", e)

    if not rows:
        print("[Warning] No candidate rows found on page.")
    # postprocess
    final = postprocess_rows(rows)
    print(f"After postprocessing: {len(final)} mappings")

    # convert to dataframe
    df = pd.DataFrame(final, columns=["Orth","Phon"])
    if df.empty:
        print("[Warning] No mappings to save.")
        return

    # sort by descending orth length to ensure digraphs are first
    df["_len"] = df["Orth"].str.len()
    df = df.sort_values(by="_len", ascending=False).drop(columns=["_len"])

    # save
    df.to_csv(OUTFILE, index=False, encoding="utf-8-sig")
    print(f"Saved {len(df)} mappings to {OUTFILE}")
    print(df.head(40))

if __name__ == "__main__":
    main()
