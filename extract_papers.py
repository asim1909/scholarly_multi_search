"""Extraction script producing an Excel sheet with two columns: Topic and APA.

The script heuristically extracts (from the first page, optionally first two pages if
needed) probable title, authors, year, venue (conference/journal), page range and DOI,
then formats a rough APA style reference. Because PDF structures vary, the output MUST
be manually verified (Google Scholar, publisher site). This avoids automated scraping
of Google Scholar (disallowed by its Terms of Service) while giving you a strong draft.

Heuristic steps:
1. Title: first plausible multi‑word line before the word 'Abstract'.
2. Authors: line with commas or ' and ' containing multiple capitalized tokens, no year.
3. Year: first four‑digit year 1950–2049.
4. DOI: pattern 10.xxxx/... (case-insensitive).
5. Venue: line containing keywords (IEEE, ACM, International, Proceedings, Journal, Conf.).
6. Pages: pattern like pp. 123-456 or 123–456.

APA formatting logic (simplified):
Authors. (Year). Title. Venue, pages. DOI

When data is missing, placeholders are inserted so you can quickly fill them.
"""

import re
from pathlib import Path
from typing import List, Optional, Dict

import pandas as pd

try:  # pragma: no cover
    from PyPDF2 import PdfReader
except ImportError:  # pragma: no cover
    raise SystemExit("PyPDF2 not installed. Run: pip install -r requirements.txt")


def read_text(pdf_path: Path, max_pages: int = 2) -> str:
    try:
        reader = PdfReader(str(pdf_path))
        collected = []
        for page in reader.pages[:max_pages]:
            try:
                collected.append(page.extract_text() or "")
            except Exception:
                continue
        return "\n".join(collected)
    except Exception as e:  # pragma: no cover
        return f"ERROR: {e}"


def normalize_spaces(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def guess_title(lines: List[str]) -> Optional[str]:
    candidates = []
    for raw in lines[:40]:
        line = raw.strip()
        if not line:
            continue
        if len(line.split()) < 3:
            continue
        if '@' in line or line.lower().startswith('issn'):
            continue
        if re.search(r"\babstract\b", line, re.I):
            break
        alpha_ratio = sum(c.isalpha() or c.isspace() for c in line) / max(1, len(line))
        if alpha_ratio > 0.6 and 3 <= len(line.split()) <= 30:
            # Exclude lines that look clearly like author lists (many commas with initials)
            if not re.search(r"\b(pp\.|doi|http)\b", line, re.I):
                candidates.append(line)
    if candidates:
        # Favor longer lines first
        candidates.sort(key=len, reverse=True)
        return candidates[0]
    return None


def guess_authors(lines: List[str]) -> Optional[str]:
    for raw in lines[:60]:
        line = normalize_spaces(raw)
        if not line:
            continue
        if len(line) > 180:
            continue
        if re.search(r"(19|20)\d{2}", line):
            continue
        if '@' in line:
            continue
        # Must contain commas or ' and '
        if (',' in line or ' and ' in line.lower()) and sum(1 for w in line.split() if w[:1].isupper()) >= 2:
            # avoid lines that look like affiliations
            if not any(k in line.lower() for k in ['university', 'department', 'school of', 'institute']):
                return line
    return None


def guess_year(text: str) -> Optional[str]:
    m = re.search(r"\b(19[5-9]\d|20[0-4]\d)\b", text)
    return m.group(0) if m else None


def guess_doi(text: str) -> Optional[str]:
    m = re.search(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, re.I)
    if m:
        return m.group(0).rstrip('.,;')
    return None


VENUE_KEYWORDS = [
    'ieee', 'acm', 'international', 'conference', 'symposium', 'proceedings', 'journal', 'transactions'
]


def guess_venue(lines: List[str]) -> Optional[str]:
    for raw in lines[:120]:
        line = normalize_spaces(raw)
        low = line.lower()
        if any(k in low for k in VENUE_KEYWORDS):
            # Avoid lines that are obviously abstracts
            if 'abstract' in low:
                continue
            # Keep moderate length
            if 8 <= len(line.split()) <= 30:
                return line
    return None


def guess_pages(text: str) -> Optional[str]:
    # Look for pp. 123-456 or 123-456 patterns
    m = re.search(r"pp?\.\s*(\d{1,4}\s*[-–]\s*\d{1,4})", text, re.I)
    if m:
        return m.group(1).replace(' ', '')
    m2 = re.search(r"\b(\d{1,4})\s*[-–]\s*(\d{1,4})\b", text)
    if m2:
        return f"{m2.group(1)}-{m2.group(2)}"
    return None


def format_authors(auth_line: Optional[str]) -> str:
    if not auth_line:
        return "[Unknown Author]"
    # Split on commas and ' and '
    parts = [p.strip() for p in re.split(r",| and ", auth_line) if p.strip()]
    formatted = []
    for p in parts[:7]:
        tokens = p.split()
        if len(tokens) >= 2:
            last = tokens[-1]
            initials = ' '.join(f"{t[0].upper()}." for t in tokens[:-1] if t and t[0].isalpha())
            formatted.append(f"{last}, {initials}")
        else:
            formatted.append(p)
    if not formatted:
        return "[Unknown Author]"
    if len(formatted) == 1:
        return formatted[0]
    return ', '.join(formatted[:-1]) + f", & {formatted[-1]}"


def build_apa(authors: str, year: Optional[str], title: Optional[str], venue: Optional[str], pages: Optional[str], doi: Optional[str]) -> str:
    parts = []
    parts.append(authors)
    parts.append(f"({year})" if year else "(n.d.)")
    parts.append(f"{title}." if title else "[Title missing].")
    if venue:
        venue_fmt = venue.rstrip('.') + '.'
        parts.append(venue_fmt)
    if pages:
        parts.append(f"pp. {pages}.")
    if doi:
        # Ensure proper DOI URL
        doi_lower = doi.lower()
        if doi_lower.startswith('10.'):
            parts.append(f"https://doi.org/{doi}")
        elif 'doi.org/' in doi_lower:
            parts.append(doi)
    return ' '.join(parts)


def process_pdf(pdf_path: Path) -> Dict[str, str]:
    text = read_text(pdf_path)
    if text.startswith('ERROR:'):
        return {'Topic': '', 'APA': f"[Failed to read: {text}]"}
    lines = text.splitlines()
    title = guess_title(lines)
    authors_line = guess_authors(lines)
    authors_fmt = format_authors(authors_line)
    year = guess_year(text)
    venue = guess_venue(lines)
    pages = guess_pages(text)
    doi = guess_doi(text)
    apa = build_apa(authors_fmt, year, title, venue, pages, doi)
    return {
        'Topic': title or '',
        'APA': apa
    }


def main():
    folder = Path(__file__).parent / 'paper'
    if not folder.exists():
        print(f"Folder not found: {folder}")
        return
    pdfs = sorted(folder.glob('*.pdf'))
    rows = []
    for pdf in pdfs:
        print(f"Processing {pdf.name} ...")
        rows.append(process_pdf(pdf))
    df = pd.DataFrame(rows, columns=['Topic', 'APA'])
    out_path = Path(__file__).parent / 'papers.xlsx'
    df.to_excel(out_path, index=False)
    print(f"Wrote {out_path} with {len(rows)} rows (Topic, APA only)")

if __name__ == '__main__':
    main()