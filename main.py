# words_service.py
import re, argparse, unicodedata
from functools import lru_cache
from typing import Iterable

WORDS_FILE = "slovy.txt"

def _norm(s: str) -> str:
    return unicodedata.normalize("NFC", s)

@lru_cache(maxsize=1)
def load_words():
    words = []
    with open(WORDS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            w = _norm(line.strip())
            if w:
                words.append((w, w.lower(), len(w)))
    return words  # list of tuples: (orig, lower, length)

def _filter_iter(
    startswith: str|None,
    endswith: str|None,
    contains: str|None,
    len_eq: int|None,
    regex: str|None
) -> Iterable[str]:
    data = load_words()
    sw = startswith.lower() if startswith else None
    ew = endswith.lower() if endswith else None
    ct = contains.lower() if contains else None
    rx = re.compile(regex) if regex else None

    for orig, low, L in data:
        if sw and not low.startswith(sw): continue
        if ew and not low.endswith(ew):   continue
        if ct and ct not in low:          continue
        if len_eq is not None and L != len_eq: continue
        if rx and not rx.search(orig):    continue
        yield orig

def search(
    startswith: str|None = None,
    endswith: str|None = None,
    contains: str|None = None,
    len_eq: int|None = None,
    regex: str|None = None,
    limit: int = 50,
    offset: int = 0
):
    it = _filter_iter(startswith, endswith, contains, len_eq, regex)
    # skip offset, take limit
    out = []
    skipped = 0
    for w in it:
        if skipped < offset:
            skipped += 1
            continue
        out.append(w)
        if len(out) >= limit:
            break
    return out

# --- CLI ---
def main():
    ap = argparse.ArgumentParser(description="Search Belarusian words from slovy.txt")
    ap.add_argument("--startswith")
    ap.add_argument("--endswith")
    ap.add_argument("--contains")
    ap.add_argument("--len", dest="len_eq", type=int)
    ap.add_argument("--regex")
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--offset", type=int, default=0)
    args = ap.parse_args()
    for w in search(**vars(args)):
        print(w)

if __name__ == "__main__":
    main()
