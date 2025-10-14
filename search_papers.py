"""Search research papers via CrossRef.

Features:
	- Columns: Topic, Year, Authors, Abstract, DOI, Link, ScholarSearch
	- Interactive mode (--interactive)
	- Append with de-duplication by DOI (--append)
	- Batch per-year export (--batch-years START-END)

Notes:
	- ScholarSearch column provides a manual Google Scholar query link (no scraping).
	- Abstracts from CrossRef may contain HTML tags which are stripped heuristically.
"""

from __future__ import annotations
import argparse
import re
import sys
import time
from pathlib import Path
from typing import List, Dict, Optional, Tuple

import pandas as pd
import requests

CROSSREF_API = "https://api.crossref.org/works"


def build_filters(year: Optional[int], from_year: Optional[int], to_year: Optional[int]) -> Dict[str, str]:
	filters = []
	if year:
		filters.append(f"from-pub-date:{year}-01-01")
		filters.append(f"until-pub-date:{year}-12-31")
	else:
		if from_year:
			filters.append(f"from-pub-date:{from_year}-01-01")
		if to_year:
			filters.append(f"until-pub-date:{to_year}-12-31")
	if not filters:
		return {}
	return {"filter": ",".join(filters)}


def query_crossref(query: str, limit: int, year: Optional[int], from_year: Optional[int], to_year: Optional[int], mailto: Optional[str]) -> List[Dict[str, str]]:
	params = {
		"query": query,
		"rows": min(limit, 200),
		"select": "title,DOI,issued,created,author,abstract",
		"sort": "relevance",
	}
	params.update(build_filters(year, from_year, to_year))
	headers = {"User-Agent": f"PaperSearch/1.0 (mailto:{mailto})" if mailto else "PaperSearch/1.0"}

	results: List[Dict[str, str]] = []
	fetched = 0
	cursor = None
	while fetched < limit:
		if limit > 200:
			params["cursor"] = "*" if cursor is None else cursor
			params["rows"] = min(200, limit - fetched)
		try:
			r = requests.get(CROSSREF_API, params=params, headers=headers, timeout=30)
		except requests.RequestException as e:
			print(f"Network error: {e}", file=sys.stderr)
			break
		if r.status_code != 200:
			print(f"CrossRef error {r.status_code}: {r.text[:200]}", file=sys.stderr)
			break
		data = r.json()
		items = data.get("message", {}).get("items", [])
		if not items:
			break
		for it in items:
			title_list = it.get("title") or []
			title = title_list[0].strip() if title_list else ""
			doi = it.get("DOI")
			link = f"https://doi.org/{doi}" if doi else ""
			year_val = None
			for key in ("issued", "created"):
				part = it.get(key, {})
				date_parts = part.get("date-parts") if isinstance(part, dict) else None
				if date_parts and isinstance(date_parts, list) and date_parts and date_parts[0]:
					first_part = date_parts[0]
					if isinstance(first_part, list) and first_part and isinstance(first_part[0], int):
						year_val = first_part[0]
						break
			from urllib.parse import quote_plus
			scholar_url = f"https://scholar.google.com/scholar?q={quote_plus(title)}"
			authors = it.get("author") or []
			author_str = ''
			if isinstance(authors, list) and authors:
				formatted = []
				for a in authors[:15]:
					given = a.get('given') or ''
					family = a.get('family') or ''
					if family and given:
						initials = ' '.join([g[0].upper() + '.' for g in given.split() if g])
						formatted.append(f"{family}, {initials}")
					elif family:
						formatted.append(family)
					elif given:
						formatted.append(given)
				author_str = '; '.join(formatted) if len(formatted) > 1 else (formatted[0] if formatted else '')
			raw_abs = it.get('abstract') or ''
			if raw_abs:
				raw_abs = re.sub(r'<[^>]+>', '', raw_abs).strip()
			results.append({
				"Topic": title,
				"Year": year_val or '',
				"Authors": author_str,
				"Abstract": raw_abs,
				"DOI": doi or '',
				"Link": link,
				"ScholarSearch": scholar_url
			})
			fetched += 1
			if fetched >= limit:
				break
		if limit <= 200:
			break
		cursor = data.get("message", {}).get("next-cursor")
		if not cursor:
			break
		time.sleep(0.2)
	return results


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
	p = argparse.ArgumentParser(description="Search papers via CrossRef and export to Excel")
	p.add_argument("--query", "-q", help="Search query / topic keywords")
	p.add_argument("--limit", "-n", type=int, default=25, help="Number of results (default 25)")
	p.add_argument("--year", "-y", type=int, help="Single publication year filter")
	p.add_argument("--from-year", type=int, dest="from_year", help="Start year (inclusive)")
	p.add_argument("--to-year", type=int, dest="to_year", help="End year (inclusive)")
	p.add_argument("--out", "-o", default="search_results.xlsx", help="Output Excel file name")
	p.add_argument("--mailto", help="Contact email for polite CrossRef requests")
	p.add_argument("--interactive", action="store_true", help="Interactive prompt mode")
	p.add_argument("--append", action="store_true", help="Append to existing Excel and de-duplicate by DOI")
	p.add_argument("--batch-years", help="Year range for batch mode, e.g. 2019-2022 (ignored if --year provided)")
	return p.parse_args(argv)


def validate_years(args: argparse.Namespace) -> None:
	if args.year and (args.from_year or args.to_year):
		raise SystemExit("Specify either --year OR a --from-year/--to-year range, not both.")
	if (args.from_year and args.to_year) and args.from_year > args.to_year:
		raise SystemExit("--from-year must be <= --to-year")


def save_excel(rows: List[Dict[str, str]], out_file: str, append: bool = False) -> Path:
	cols = ["Topic", "Year", "Authors", "Abstract", "DOI", "Link", "ScholarSearch"]
	new_df = pd.DataFrame(rows, columns=cols)
	path = Path(out_file).resolve()
	if append and path.exists():
		try:
			old = pd.read_excel(path)
			combined = pd.concat([old, new_df], ignore_index=True)
			if 'DOI' in combined.columns:
				before = len(combined)
				combined = combined.drop_duplicates(subset=['DOI'], keep='first')
				after = len(combined)
				print(f"De-duplicated by DOI: removed {before - after} duplicates.")
			else:
				combined = combined.drop_duplicates()
			combined.to_excel(path, index=False)
			return path
		except Exception as e:
			print(f"Append failed ({e}); writing new file.")
	new_df.to_excel(path, index=False)
	return path


def parse_year_range(range_str: str) -> Tuple[int, int]:
	parts = range_str.split('-', 1)
	if len(parts) != 2:
		raise ValueError("Invalid range format; expected startYear-endYear")
	start = int(parts[0])
	end = int(parts[1])
	if start > end:
		raise ValueError("Start year must be <= end year")
	return start, end


def interactive_fill(args: argparse.Namespace) -> argparse.Namespace:
	if not args.query:
		args.query = input("Enter research topic / keywords: ").strip()
	if not args.limit or args.limit <= 0:
		try:
			args.limit = int(input("Number of results (default 25): ") or "25")
		except ValueError:
			args.limit = 25
	if not args.year and not (args.from_year or args.to_year):
		year_range = input("Enter year or range (e.g. 2021 or 2019-2023, leave blank for all): ").strip()
		if year_range:
			if '-' in year_range:
				parts = year_range.split('-', 1)
				try:
					args.from_year = int(parts[0])
					args.to_year = int(parts[1])
				except ValueError:
					print("Invalid range, ignoring.")
			else:
				try:
					args.year = int(year_range)
				except ValueError:
					print("Invalid year, ignoring.")
	if not args.batch_years and not args.year and not (args.from_year or args.to_year):
		yr_batch = input("Batch per-year export? Enter range (e.g. 2019-2022) or leave blank: ").strip()
		if yr_batch:
			args.batch_years = yr_batch
	out_in = input(f"Output file name [{args.out}]: ") or args.out
	args.out = out_in
	return args


def main(argv: Optional[List[str]] = None) -> int:
	args = parse_args(argv)
	if args.interactive or not args.query:
		args = interactive_fill(args)
	validate_years(args)
	if args.limit <= 0:
		print("--limit must be positive", file=sys.stderr)
		return 1
	if not args.query:
		print("No query provided.")
		return 1

	# Batch per-year export
	if args.batch_years and not args.year:
		try:
			start, end = parse_year_range(args.batch_years)
		except ValueError as e:
			print(f"Batch years error: {e}")
			return 1
		combined_rows: List[Dict[str, str]] = []
		total = 0
		for yr in range(start, end + 1):
			print(f"Fetching year {yr} ...")
			rows_year = query_crossref(args.query, args.limit, yr, None, None, args.mailto)
			if not rows_year:
				print(f"  Year {yr}: no results")
				continue
			combined_rows.extend(rows_year)
			total += len(rows_year)
		if not combined_rows:
			print("No results in the specified batch range.")
			return 0
		out_path = save_excel(combined_rows, args.out, append=args.append)
		print(f"Batch complete. Collected {total} rows across years {start}-{end} in {out_path}")
		return 0

	print(f"Querying CrossRef for: '{args.query}' (limit={args.limit})")
	if args.year:
		print(f" Year: {args.year}")
	elif args.from_year or args.to_year:
		print(f" Year range: {args.from_year or ''} - {args.to_year or ''}")
	rows = query_crossref(args.query, args.limit, args.year, args.from_year, args.to_year, args.mailto)
	if not rows:
		print("No results returned.")
		return 0
	out_path = save_excel(rows, args.out, append=args.append)
	print(f"Saved {len(rows)} rows to {out_path}")
	return 0


if __name__ == "__main__":  # pragma: no cover
	raise SystemExit(main())

