#!/usr/bin/env python3
"""Analyze PDF page counts and filter papers with less than 7 pages."""

from pathlib import Path
import pandas as pd
from PyPDF2 import PdfReader

def get_pdf_page_count(pdf_path):
    """Get page count from PDF file."""
    try:
        reader = PdfReader(pdf_path)
        return len(reader.pages)
    except Exception as e:
        return None

def analyze_pdfs(pdf_folder, excel_file=None):
    """Analyze PDFs in folder and create report."""
    
    pdf_dir = Path(pdf_folder)
    if not pdf_dir.exists():
        print(f"Error: {pdf_folder} not found")
        return None
    
    # Find all PDFs
    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"\n📊 Found {len(pdf_files)} PDF files to analyze\n")
    
    results = []
    
    for pdf_path in sorted(pdf_files):
        page_count = get_pdf_page_count(pdf_path)
        
        if page_count is not None:
            results.append({
                "Filename": pdf_path.name,
                "Pages": page_count,
                "Size (MB)": pdf_path.stat().st_size / (1024 * 1024),
                "Short": "✅" if page_count < 7 else "❌"
            })
            
            status = "✅ SHORT" if page_count < 7 else "❌ LONG"
            print(f"{status} | {pdf_path.name[:70]:70} | {page_count} pages")
        else:
            print(f"⚠️  ERROR | {pdf_path.name[:70]:70} | Could not read")
    
    if results:
        # Create dataframe
        df = pd.DataFrame(results)
        
        # Filter for papers with less than 7 pages
        short_papers = df[df['Pages'] < 7].sort_values('Pages')
        
        print(f"\n{'='*100}")
        print(f"📄 Papers with LESS THAN 7 PAGES: {len(short_papers)}")
        print(f"{'='*100}\n")
        
        for idx, row in short_papers.iterrows():
            print(f"✅ {row['Filename']} | {row['Pages']} pages | {row['Size (MB)']:.2f} MB")
        
        # Save report
        report_file = f"{pdf_folder}_analysis.xlsx"
        df.to_excel(report_file, index=False)
        print(f"\n📁 Full analysis saved to: {report_file}")
        
        # Save short papers list
        short_file = f"{pdf_folder}_short_papers.xlsx"
        short_papers.to_excel(short_file, index=False)
        print(f"📁 Short papers list saved to: {short_file}\n")
        
        return short_papers
    else:
        print("No PDFs found to analyze")
        return None

if __name__ == "__main__":
    import sys
    
    folder = sys.argv[1] if len(sys.argv) > 1 else "mental_health_apps_papers"
    
    analyze_pdfs(folder)
