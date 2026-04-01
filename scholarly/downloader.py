"""Download research papers from URLs and save locally."""

import os
import re
import time
from pathlib import Path
from typing import Optional, Dict, List
import requests
import pandas as pd


class PaperDownloader:
    """Handle downloading and organizing research papers."""
    
    def __init__(self, download_dir: str = "papers"):
        """Initialize downloader with target directory.
        
        Args:
            download_dir: Directory to store downloaded papers (default: 'papers')
        """
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "ScholarlyMultiSearch/0.1 (Research Paper Downloader)"
        })
        
    def sanitize_filename(self, filename: str, max_length: int = 100) -> str:
        """Sanitize filename for use in filesystem.
        
        Args:
            filename: Original filename
            max_length: Maximum filename length
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
        sanitized = re.sub(invalid_chars, '', filename)
        # Replace multiple spaces with single space
        sanitized = re.sub(r'\s+', ' ', sanitized).strip()
        # Truncate if too long
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length].rsplit(' ', 1)[0]
        return sanitized or "paper"
    
    def download_paper(self, url: str, title: str = "", retries: int = 3) -> Optional[str]:
        """Download a paper from URL.
        
        Args:
            url: URL to download from
            title: Paper title (used for filename)
            retries: Number of retry attempts
            
        Returns:
            Path to downloaded file if successful, None otherwise
        """
        if not url:
            return None
            
        # Create filename from title or URL
        if title:
            filename = f"{self.sanitize_filename(title)}.pdf"
        else:
            filename = f"paper_{int(time.time())}.pdf"
        
        filepath = self.download_dir / filename
        
        # Skip if already downloaded
        if filepath.exists():
            print(f"  ✓ Already downloaded: {filename}")
            return str(filepath)
        
        # Try downloading with retries
        for attempt in range(retries):
            try:
                print(f"  Downloading: {filename}...", end="", flush=True)
                response = self.session.get(url, timeout=30, allow_redirects=True)
                response.raise_for_status()
                
                # Check if response is PDF
                content_type = response.headers.get('content-type', '').lower()
                if 'pdf' not in content_type and 'application/octet-stream' not in content_type:
                    # Still try if it has typical PDF magic bytes
                    if not response.content.startswith(b'%PDF'):
                        print(f" SKIP (not a PDF)")
                        return None
                
                # Save file
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                file_size = filepath.stat().st_size / 1024  # KB
                print(f" ✓ ({file_size:.1f} KB)")
                return str(filepath)
                
            except requests.exceptions.Timeout:
                print(f" TIMEOUT (attempt {attempt + 1}/{retries})", end="")
                if attempt < retries - 1:
                    print(", retrying...")
                    time.sleep(2)
                else:
                    print(" FAILED")
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 403:
                    print(f" BLOCKED (403 Forbidden)")
                    return None
                elif attempt < retries - 1:
                    print(f" HTTP ERROR {e.response.status_code}, retrying...")
                    time.sleep(2)
                else:
                    print(f" HTTP ERROR {e.response.status_code}")
            except Exception as e:
                if attempt < retries - 1:
                    print(f" ERROR: {type(e).__name__}, retrying...")
                    time.sleep(1)
                else:
                    print(f" FAILED: {str(e)}")
        
        return None
    
    def download_from_excel(self, excel_file: str, output_file: str = None, 
                           max_downloads: int = None) -> Dict[str, any]:
        """Download papers from an Excel file with paper data.
        
        Args:
            excel_file: Path to Excel file with paper data
            output_file: Path to save updated Excel with download status
            max_downloads: Maximum papers to download (None for all)
            
        Returns:
            Dictionary with download statistics
        """
        if not Path(excel_file).exists():
            print(f"Error: File '{excel_file}' not found")
            return {"total": 0, "downloaded": 0, "failed": 0}
        
        try:
            df = pd.read_excel(excel_file)
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return {"total": 0, "downloaded": 0, "failed": 0}
        
        stats = {
            "total": len(df),
            "downloaded": 0,
            "failed": 0,
            "skipped": 0,
        }
        
        # Add download status column if not exists
        if "Downloaded" not in df.columns:
            df["Downloaded"] = ""
        
        limit = min(max_downloads, len(df)) if max_downloads else len(df)
        
        print(f"\nDownloading papers from '{excel_file}'...")
        print(f"Found {len(df)} papers. Starting download of {limit} papers.\n")
        
        for idx, row in df.head(limit).iterrows():
            title = str(row.get("Title", f"Paper_{idx}"))
            link = str(row.get("Link", ""))
            source = row.get("Source", "Unknown")
            
            print(f"[{idx + 1}/{limit}] {title[:60]}... ({source})")
            
            if not link or link.lower() in ["", "nan"]:
                print("  SKIP (no link)")
                stats["skipped"] += 1
                df.at[idx, "Downloaded"] = "No"
                continue
            
            # Handle different source types
            result = None
            
            if "arxiv.org" in link and "pdf" not in link:
                # arXiv abstracts - convert to PDF URL
                arxiv_id = link.split("/abs/")[-1]
                pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
                result = self.download_paper(pdf_url, title)
            elif "arxiv.org/pdf" in link:
                result = self.download_paper(link, title)
            elif "semanticscholar.org" in link:
                # Semantic Scholar links don't have direct PDFs usually
                print("  SKIP (Semantic Scholar links require external access)")
                stats["skipped"] += 1
                df.at[idx, "Downloaded"] = "No"
                continue
            else:
                # Try direct download
                result = self.download_paper(link, title)
            
            if result:
                stats["downloaded"] += 1
                df.at[idx, "Downloaded"] = "Yes"
            else:
                stats["failed"] += 1
                df.at[idx, "Downloaded"] = "No"
            
            # Be nice to servers - throttle requests
            time.sleep(1)
        
        # Save updated Excel if requested
        if output_file:
            try:
                df.to_excel(output_file, index=False)
                print(f"\nUpdated Excel saved to '{output_file}'")
            except Exception as e:
                print(f"Error saving updated Excel: {e}")
        
        print(f"\n{'='*60}")
        print(f"Download Summary:")
        print(f"  Total papers: {stats['total']}")
        print(f"  Downloaded: {stats['downloaded']}")
        print(f"  Failed: {stats['failed']}")
        print(f"  Skipped: {stats['skipped']}")
        print(f"  Papers saved to: {self.download_dir.absolute()}")
        print(f"{'='*60}\n")
        
        return stats


def download_command(excel_file: str, download_dir: str = "papers", 
                     max_downloads: int = None, update_excel: bool = False):
    """Command-line entry point for downloading papers."""
    downloader = PaperDownloader(download_dir)
    output_file = excel_file.replace(".xlsx", "_with_downloads.xlsx") if update_excel else None
    downloader.download_from_excel(excel_file, output_file, max_downloads)
