#!/usr/bin/env python3
# clean_greek_orthography.py
# Usage: python clean_greek_orthography.py
# Expects a CSV named greek_raw.csv (or change INPUT_FILE below).
#
# Produces: ell-Grek.csv (Orth,Phon) cleaned and deduped.

import csv
import re
import unicodedata
import os
import sys

INPUT_FILE = "ell-Grek.csv"   # change to your filename
OUTPUT_FILE = "0ell-Grek.csv"
ENC = "utf-8-sig"

# Unicode ranges for Greek letters:
GREEK_RE = re.compile(r'[\u0370-\u03FF\u1F00-\u1FFF]+')  # sequences of Greek letters
# bracketed IPA like [a], possibly multiple in one field
BRACKET_RE = re.compile(r'\[([^\]]+)\]')
SLASH_RE = re.compile(r'/([^/]+)/')
# Acceptable separators for variants
SPLIT_VARIANTS_RE = re.compile(r'\s*(?:,|;|/|~|\bor\b|\|)\s*', flags=re.IGNORECASE)

def normalize_text(s):
    if s is None:
        return ""
    s = str(s)
    s = s.strip()
    s = unicodedata.normalize("NFC", s)
    return s

def extract_orth_candidates(raw_orth):
    """
    Return a list of orth candidates (Greek letter sequences or slash-delimited tokens).
    """
    orth = normalize_text(raw_orth)
    if not orth:
        return []
    # if it's a control prefix like lo,li etc -> skip
    lower = orth.lower()
    if lower.startswith("lo") or lower.startswith("li") or lower.startswith("note") or lower.startswith("^"):
        return []

    # If orth contains explicit slashed form e.g. "/i/" or starts/ends with '/'
    mslash = SLASH_RE.search(orth)
    if mslash:
        return [mslash.group(1)]

    # find Greek sequences (prefer first) - but return all distinct sequences of length <=3
    seqs = GREEK_RE.findall(orth)
    seqs = [s for s in seqs if 0 < len(s) <= 3]  # keep up to length 3 (letters/digraphs)
    if seqs:
        # return unique preserving order
        seen = set()
        out = []
        for s in seqs:
            if s not in seen:
                seen.add(s)
                out.append(s)
        return out

    # fallback: if orth looks like ASCII token but short (e.g., 'i' or 'o') keep it
    if re.fullmatch(r"[A-Za-z0-9ǀ\-\u0301\_]{1,3}", orth):
        return [orth]

    return []

def extract_phon_variants(raw_phon):
    """
    Given the raw Phon column text, return a list of cleaned phon variants (strings).
    Looks for [...] bracketed IPA, /.../ slashed IPA, or plain tokens.
    """
    phon = normalize_text(raw_phon)
    if not phon:
        return []

    variants = []

    # 1) collect all bracketed groups [ ... ]
    for br in BRACKET_RE.findall(phon):
        # split internal comma-separated variants too
        for part in SPLIT_VARIANTS_RE.split(br):
            p = part.strip()
            if p:
                variants.append(p)

    # 2) collect /.../ slashed groups
    for sl in SLASH_RE.findall(phon):
        for part in SPLIT_VARIANTS_RE.split(sl):
            p = part.strip()
            if p:
                variants.append(p)

    # 3) if no bracket or slash captured, fallback to splitting the whole cell
    if not variants:
        # remove footnote markers like ^, digits in parentheses
        temp = re.sub(r'\^\w+','', phon)
        temp = re.sub(r'\(.*?\)', '', temp)
        # split on separators
        for part in SPLIT_VARIANTS_RE.split(temp):
            p = part.strip()
            # discard purely English commentary tokens like 'though', 'often', 'now'
            if not p:
                continue
            if len(p) > 0 and re.search(r'[A-Za-z]{4,}', p) and not re.search(r'[\u0370-\u03FF\u1F00-\u1FFF\[\]\/ɡɣθðʃʒŋɲɸχɬɾˈˌəɔɛɑɪɯɨʊʉʎʝː]', p):
                continue
            variants.append(p)

    # final cleaning: remove stray punctuation, normalize spaces, strip leading/trailing punctuation
    cleaned = []
    for v in variants:
        v = v.strip()
        v = v.strip('\"\'')            # remove quotes
        v = v.strip('.,;:')            # trailing punctuation
        v = v.replace('  ', ' ')
        v = v.replace(u'\u200b', '')   # zero-width
        v = unicodedata.normalize("NFC", v)
        if v and v not in cleaned:
            cleaned.append(v)
    return cleaned

def is_noise_row(orth_candidates, phon_variants, raw_orth, raw_phon):
    """
    Decide whether a row is noise (example text, long commentary).
    We drop rows where no Greek orth candidate and phon doesn't look like IPA.
    """
    if not orth_candidates:
        return True
    # if all orth candidates are ASCII words longer than 3 -> noise
    ascii_long = all(re.fullmatch(r'[A-Za-z0-9]+', o) and len(o) > 3 for o in orth_candidates)
    if ascii_long and not phon_variants:
        return True
    # if phon_variants are mostly English words like 'though', 'often', skip
    if phon_variants:
        # if every variant contains only letters and length>3 and not IPA symbols -> likely noise
        non_ipa_count = 0
        for v in phon_variants:
            # consider IPA presence if contains non-ascii IPA chars or symbols like 'ˈ', 'ː', 'ɣ', 'ɲ'
            if not re.search(r'[^A-Za-z0-9 ,.-]', v) and len(re.sub(r'[^A-Za-z]','', v))>3:
                non_ipa_count += 1
        if non_ipa_count == len(phon_variants) and non_ipa_count > 0:
            return True
    return False

def main():
    if not os.path.exists(INPUT_FILE):
        print("Input file not found:", INPUT_FILE)
        sys.exit(1)

    pairs = []  # list of (orth, phon)

    with open(INPUT_FILE, newline='', encoding=ENC) as f:
        reader = csv.reader(f)
        header = next(reader, None)
        # handle if header merged or not
        # assume header has at least 2 cols; if first header cell equals 'Orth' good, else treat it same
        for row in reader:
            if not row:
                continue
            # some CSV lines may have many commas; join extras back into second column
            if len(row) == 1:
                raw_orth = row[0]
                raw_phon = ""
            else:
                raw_orth = row[0]
                raw_phon = ",".join(row[1:])  # preserve commas in phon field
            raw_orth = normalize_text(raw_orth)
            raw_phon = normalize_text(raw_phon)

            orth_candidates = extract_orth_candidates(raw_orth)
            phon_variants = extract_phon_variants(raw_phon)

            if is_noise_row(orth_candidates, phon_variants, raw_orth, raw_phon):
                continue

            # create mapping entries for each orth candidate × each phon variant
            for orth in orth_candidates:
                for phon in phon_variants:
                    pairs.append((orth, phon))

    # dedupe while preserving order, but keep first occurrence
    seen = set()
    final = []
    for o,p in pairs:
        key = (o, p)
        if key not in seen:
            seen.add(key)
            final.append((o,p))

    # If empty, warn and exit
    if not final:
        print("No mappings extracted - check the input file / format.")
        sys.exit(0)

    # Sort by orth length descending (so digraphs come before single letters)
    final.sort(key=lambda x: len(x[0]), reverse=True)

    # Write output CSV
    with open(OUTPUT_FILE, "w", encoding=ENC, newline='') as out:
        writer = csv.writer(out)
        writer.writerow(["Orth","Phon"])
        for o,p in final:
            writer.writerow([o, p])

    print(f"Saved {len(final)} mappings to {OUTPUT_FILE}")
    # print first 40 for quick inspection
    for o,p in final[:40]:
        print(f"{o} -> {p}")

if __name__ == "__main__":
    main()
