import time
import pandas as pd
from .sources.crossref import search_crossref
from .sources.arxiv import search_arxiv
from .sources.semanticscholar import search_semanticscholar
from .aggregator import deduplicate
from .downloader import PaperDownloader

def run(query: str, num_results: int, out_file: str):
    print(f"Searching CrossRef for '{query}'...")
    crossref_rows = search_crossref(query, num_results)
    print(f"Found {len(crossref_rows)} from CrossRef.")
    time.sleep(1)
    print(f"Searching arXiv for '{query}'...")
    arxiv_rows = search_arxiv(query, num_results)
    print(f"Found {len(arxiv_rows)} from arXiv.")
    time.sleep(1)
    print(f"Searching Semantic Scholar for '{query}'...")
    semsch_rows = search_semanticscholar(query, num_results)
    print(f"Found {len(semsch_rows)} from Semantic Scholar.")

    all_rows = crossref_rows + arxiv_rows + semsch_rows
    deduped = deduplicate(all_rows)
    print(f"Total after deduplication: {len(deduped)}")

    df = pd.DataFrame(deduped)
    df.to_excel(out_file, index=False)
    print(f"Saved to {out_file}")

def download_papers(excel_file: str, download_dir: str = "papers", max_downloads: int = None, update_excel: bool = False):
    """Download papers from Excel file."""
    downloader = PaperDownloader(download_dir)
    output_file = excel_file.replace(".xlsx", "_with_downloads.xlsx") if update_excel else None
    downloader.download_from_excel(excel_file, output_file, max_downloads)

def main():
    import argparse
    import sys
    
    parser = argparse.ArgumentParser(description="Multi-source research paper search and download tool")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Search command
    search_parser = subparsers.add_parser("search", help="Search for research papers")
    search_parser.add_argument("-q", "--query", help="Search topic")
    search_parser.add_argument("-n", "--num-results", type=int, help="Max results per source")
    search_parser.add_argument("-o", "--out", help="Output Excel filename")
    
    # Download command
    download_parser = subparsers.add_parser("download", help="Download papers from Excel file")
    download_parser.add_argument("-f", "--file", required=True, help="Input Excel file with paper data")
    download_parser.add_argument("-d", "--dir", default="papers", help="Download directory (default: papers)")
    download_parser.add_argument("-m", "--max", type=int, help="Maximum papers to download")
    download_parser.add_argument("--update-excel", action="store_true", help="Save updated Excel with download status")
    
    args = parser.parse_args()
    
    # If no command, default to search (backward compatibility)
    if not args.command:
        args.command = "search"
        # Shift arguments for search if no command was specified
        sys.argv.insert(1, "search")
        args, remaining = parser.parse_known_args()
    
    if args.command == "download":
        download_papers(args.file, args.dir, args.max, args.update_excel)
    else:  # search
        if not args.query:
            args.query = input("Enter your research topic: ").strip()
            while not args.query:
                args.query = input("Topic cannot be empty. Enter your research topic: ").strip()
        if not args.num_results:
            while True:
                n = input("How many results per source? (default 50): ").strip()
                if not n:
                    args.num_results = 50
                    break
                try:
                    args.num_results = int(n)
                    if args.num_results > 0:
                        break
                    else:
                        print("Please enter a positive integer.")
                except ValueError:
                    print("Please enter a valid number.")
        if not args.out:
            args.out = input("Output Excel filename? (default papers_all_sources.xlsx): ").strip()
            if not args.out:
                args.out = "papers_all_sources.xlsx"

        run(args.query, args.num_results, args.out)

if __name__ == "__main__":
    main()
