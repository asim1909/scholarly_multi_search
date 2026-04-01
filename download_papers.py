#!/usr/bin/env python3
"""Download research papers from Excel file.

Usage:
    # Download papers from Excel file
    python download_papers.py papers_all_sources.xlsx
    
    # Download to custom directory
    python download_papers.py papers_all_sources.xlsx --dir my_papers
    
    # Download with limit and save updated Excel
    python download_papers.py papers_all_sources.xlsx --max 20 --update-excel
"""

import sys
import argparse
from pathlib import Path
from scholarly.downloader import PaperDownloader

def main():
    parser = argparse.ArgumentParser(
        description="Download research papers from Excel file",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download all papers from Excel
  python download_papers.py research_papers.xlsx
  
  # Download to custom folder
  python download_papers.py research_papers.xlsx --dir my_papers
  
  # Download max 20 papers and save with download status
  python download_papers.py research_papers.xlsx --max 20 --update-excel
        """
    )
    
    parser.add_argument("file", help="Excel file with paper data")
    parser.add_argument("--dir", "-d", default="papers", help="Download directory (default: papers)")
    parser.add_argument("--max", "-m", type=int, help="Maximum papers to download")
    parser.add_argument("--update-excel", action="store_true", help="Save updated Excel with download status")
    
    args = parser.parse_args()
    
    # Verify file exists
    excel_file = Path(args.file)
    if not excel_file.exists():
        print(f"Error: File '{args.file}' not found")
        sys.exit(1)
    
    # Download papers
    downloader = PaperDownloader(args.dir)
    output_file = str(excel_file).replace(".xlsx", "_with_downloads.xlsx") if args.update_excel else None
    stats = downloader.download_from_excel(str(excel_file), output_file, args.max)
    
    # Exit with appropriate code
    sys.exit(0 if stats["downloaded"] > 0 or stats["skipped"] > 0 else 1)

if __name__ == "__main__":
    main()
