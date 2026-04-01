#!/usr/bin/env python3
"""
Test/demo script for the paper download feature.

This script demonstrates the download functionality with sample data.
"""

import json
import tempfile
from pathlib import Path
import pandas as pd
from scholarly.downloader import PaperDownloader


def create_sample_excel():
    """Create a sample Excel file with test papers."""
    
    # Sample papers with real arXiv links
    sample_data = [
        {
            "Title": "Attention Is All You Need",
            "Authors": "Vaswani et al.",
            "Year": "2017",
            "Abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks",
            "DOI": "10.48550/arXiv.1706.03762",
            "Link": "https://arxiv.org/abs/1706.03762",
            "Source": "arXiv"
        },
        {
            "Title": "BERT Pre-training of Deep Bidirectional Transformers for Language Understanding",
            "Authors": "Devlin et al.",
            "Year": "2019",
            "Abstract": "We introduce a new language representation model called BERT",
            "DOI": "10.48550/arXiv.1810.04805",
            "Link": "https://arxiv.org/abs/1810.04805",
            "Source": "arXiv"
        },
        {
            "Title": "Language Models are Unsupervised Multitask Learners",
            "Authors": "Radford et al.",
            "Year": "2019",
            "Abstract": "Natural language processing tasks are typically approached with supervised learning",
            "DOI": "",
            "Link": "https://arxiv.org/abs/1907.05887",
            "Source": "arXiv"
        }
    ]
    
    # Create Excel file
    df = pd.DataFrame(sample_data)
    excel_file = "sample_papers.xlsx"
    df.to_excel(excel_file, index=False)
    print(f"✓ Created sample Excel file: {excel_file}")
    return excel_file


def demo_downloader():
    """Demonstrate the downloader functionality."""
    
    print("\n" + "="*60)
    print("📥 Paper Downloader Demo")
    print("="*60 + "\n")
    
    # Create sample Excel
    excel_file = create_sample_excel()
    
    print("\nSample Excel Contents:")
    df = pd.read_excel(excel_file)
    print(df[["Title", "Source"]].to_string(index=False))
    
    # Create downloader
    print("\n\n" + "-"*60)
    print("Starting download to 'demo_papers/' directory...")
    print("-"*60 + "\n")
    
    downloader = PaperDownloader(download_dir="demo_papers")
    
    # Note: This is a demo that will attempt real downloads
    # You can comment out or limit for testing
    print("Note: This will attempt real downloads from arXiv (may take a moment)...\n")
    
    # Download with limit for demo
    stats = downloader.download_from_excel(
        excel_file=excel_file,
        output_file="sample_papers_updated.xlsx",
        max_downloads=2  # Limit for demo
    )
    
    # Print results
    print("\nDownload Demo Complete!")
    print(f"Check 'demo_papers/' folder for downloaded papers")
    print(f"Check 'sample_papers_updated.xlsx' for download status")


def test_filename_sanitization():
    """Test filename sanitization function."""
    
    print("\n" + "="*60)
    print("🧪 Testing Filename Sanitization")
    print("="*60 + "\n")
    
    downloader = PaperDownloader()
    
    test_cases = [
        "Normal Title",
        "Title with <illegal> characters: /\\|?*",
        "Title with \"quotes\" and 'apostrophes'",
        "Very " + "long " * 20 + "title that exceeds maximum length",
        "   Whitespace   Handling   ",
        "Title-with-dashes-and_underscores"
    ]
    
    for test in test_cases:
        sanitized = downloader.sanitize_filename(test, max_length=100)
        print(f"Input:  {test[:50]}")
        print(f"Output: {sanitized}")
        print()


def test_arxiv_url_conversion():
    """Test arXiv URL conversion logic."""
    
    print("\n" + "="*60)
    print("🧪 Testing arXiv URL Conversion")
    print("="*60 + "\n")
    
    test_urls = [
        ("https://arxiv.org/abs/1706.03762", "https://arxiv.org/pdf/1706.03762.pdf"),
        ("https://arxiv.org/pdf/1810.04805.pdf", "https://arxiv.org/pdf/1810.04805.pdf"),
        ("https://example.com/paper.pdf", "https://example.com/paper.pdf"),
    ]
    
    for original, expected in test_urls:
        if "arxiv.org" in original and "pdf" not in original:
            arxiv_id = original.split("/abs/")[-1]
            converted = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        else:
            converted = original
        
        status = "✓" if converted == expected else "✗"
        print(f"{status} {original}")
        if converted != expected:
            print(f"  Expected: {expected}")
            print(f"  Got:      {converted}")
        print()


def main():
    """Run demonstrations."""
    
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*58 + "║")
    print("║" + "  Paper Downloader - Test & Demo Script".center(58) + "║")
    print("║" + " "*58 + "║")
    print("╚" + "="*58 + "╝")
    
    # Run tests
    test_filename_sanitization()
    test_arxiv_url_conversion()
    
    # Run demo (optional - comment out if you don't want real downloads)
    try:
        response = input("\nRun live download demo? (y/n): ").strip().lower()
        if response == 'y':
            demo_downloader()
        else:
            print("\nSkipping live demo. You can run it later with:")
            print("  python test_downloader.py")
    except KeyboardInterrupt:
        print("\nDemo cancelled by user")
    
    print("\n" + "="*60)
    print("✓ Tests completed!")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
