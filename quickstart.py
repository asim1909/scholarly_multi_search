#!/usr/bin/env python3
"""
Quick Start Guide - Paper Download Feature
Run this to get started with downloading research papers!
"""

def show_menu():
    print("\n" + "="*70)
    print("  📚 SCHOLARLY MULTI-SEARCH - PAPER DOWNLOAD FEATURE")
    print("="*70)
    print("\nChoose an option:")
    print("\n  1. Search for papers (new research)")
    print("  2. Download papers from existing Excel file")
    print("  3. View help and examples")
    print("  4. Exit")
    print("\n" + "-"*70)


def option_search():
    import subprocess
    print("\n📡 Starting Paper Search...\n")
    subprocess.run(["python", "-m", "scholarly.cli", "search"])


def option_download():
    from pathlib import Path
    import subprocess
    
    print("\n📥 Paper Download\n")
    excel_file = input("Enter Excel file path (or press Enter to browse): ").strip()
    
    if not excel_file:
        # Try to find Excel files in current directory
        excel_files = list(Path(".").glob("*.xlsx"))
        if excel_files:
            print("\nFound Excel files:")
            for i, f in enumerate(excel_files, 1):
                print(f"  {i}. {f.name}")
            choice = input("Select file number: ").strip()
            try:
                excel_file = str(excel_files[int(choice)-1])
            except:
                print("Invalid selection")
                return
        else:
            print("No Excel files found in current directory")
            return
    
    # Check options
    max_papers = input("Max papers to download (press Enter for all): ").strip()
    update_excel = input("Save download status in Excel? (y/n, default: n): ").strip().lower() == 'y'
    
    # Build command
    cmd = ["python", "download_papers.py", excel_file]
    if max_papers:
        cmd.extend(["--max", max_papers])
    if update_excel:
        cmd.append("--update-excel")
    
    print()
    subprocess.run(cmd)


def option_help():
    help_text = """
╔════════════════════════════════════════════════════════════════════╗
║                          QUICK HELP GUIDE                         ║
╚════════════════════════════════════════════════════════════════════╝

🔍 SEARCHING FOR PAPERS
──────────────────────────────────────────────────────────────────────
Command: python -m scholarly.cli search -q "TOPIC" -n 50 -o FILE.xlsx

Example:
  python -m scholarly.cli search -q "machine learning" -n 100 -o ml_papers.xlsx

This will search 3 sources (CrossRef, arXiv, Semantic Scholar) and create
an Excel file with results.

📥 DOWNLOADING PAPERS
──────────────────────────────────────────────────────────────────────
Command: python download_papers.py FILE.xlsx [OPTIONS]

Basic:
  python download_papers.py ml_papers.xlsx
  └─ Downloads all papers to 'papers/' folder

With Options:
  python download_papers.py ml_papers.xlsx --dir my_research --max 50
  └─ Downloads max 50 papers to 'my_research/' folder

Track Progress:
  python download_papers.py ml_papers.xlsx --update-excel
  └─ Creates 'ml_papers_with_downloads.xlsx' with status

📊 COMPLETE WORKFLOW
──────────────────────────────────────────────────────────────────────
1. Search:   python -m scholarly.cli search -q "AI" -n 50 -o ai.xlsx
2. Download: python download_papers.py ai.xlsx --max 25
3. Use:      All papers saved in papers/ folder!

🎯 QUICK EXAMPLES
──────────────────────────────────────────────────────────────────────
# Search specific topic, limited results
python -m scholarly.cli search -q "quantum computing" -n 25 -o quantum.xlsx

# Download only 10 papers from previous results
python download_papers.py previous_search.xlsx --max 10

# Download to named folder
python download_papers.py papers.xlsx --dir my_papers

# Download with tracking
python download_papers.py papers.xlsx --max 50 --update-excel

💡 TIPS
──────────────────────────────────────────────────────────────────────
• Start small: Use --max 5-10 to test downloads first
• Check progress: Updated Excel shows which papers downloaded
• arXiv is reliable: Most arXiv papers should download successfully
• Large batches: 50+ papers may take 10-20 minutes
• Server friendly: Tool adds 1-second delays between downloads

📖 DOCUMENTATION
──────────────────────────────────────────────────────────────────────
For detailed documentation, see:
  • DOWNLOAD_GUIDE.md - Complete download guide
  • README.md - Full project documentation
  • IMPLEMENTATION_SUMMARY.md - Technical details

❓ TROUBLESHOOTING
──────────────────────────────────────────────────────────────────────
Issue: "No Excel files found"
└─ Run search first to create an Excel file

Issue: Some papers fail to download
└─ Check if links are valid, some papers may be behind paywalls

Issue: Downloads are slow
└─ This is normal; server throttling helps avoid blocks

Issue: File not found
└─ Check Excel file path is in current directory

═════════════════════════════════════════════════════════════════════
"""
    print(help_text)


def main():
    while True:
        show_menu()
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            option_search()
        elif choice == "2":
            option_download()
        elif choice == "3":
            option_help()
        elif choice == "4":
            print("\nGoodbye! 👋\n")
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    import sys
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Goodbye! 👋\n")
        sys.exit(0)
