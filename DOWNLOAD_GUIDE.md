# 📥 Paper Download Feature - Usage Guide

## Overview

The new paper download feature allows you to automatically download research papers from sources like arXiv, CrossRef, and other repositories. Papers are organized in a dedicated folder with meaningful filenames.

## Quick Start

### 1. Search for Papers
```bash
python -m scholarly.cli search -q "your research topic" -n 50 -o papers.xlsx
```

### 2. Download Papers
```bash
python download_papers.py papers.xlsx
```

That's it! All papers will be saved to a `papers/` folder.

## Detailed Usage

### Method 1: Using download_papers.py (Recommended)

**Basic download:**
```bash
python download_papers.py research_results.xlsx
```

**Download with options:**
```bash
# Download to custom directory
python download_papers.py research_results.xlsx --dir ./my_papers

# Download maximum 20 papers only
python download_papers.py research_results.xlsx --max 20

# Download and save update status in Excel
python download_papers.py research_results.xlsx --update-excel

# Combine multiple options
python download_papers.py research_results.xlsx --dir ./archive --max 50 --update-excel
```

### Method 2: Using CLI

**Via scholarly CLI:**
```bash
python -m scholarly.cli download -f papers.xlsx

python -m scholarly.cli download -f papers.xlsx --dir papers_backup --max 30 --update-excel
```

### Method 3: In Python Code

```python
from scholarly.downloader import PaperDownloader

# Create downloader instance
downloader = PaperDownloader(download_dir="my_papers")

# Download from Excel file
stats = downloader.download_from_excel(
    excel_file="research_papers.xlsx",
    output_file="research_papers_updated.xlsx",  # Optional
    max_downloads=50  # Optional
)

print(f"Downloaded: {stats['downloaded']} papers")
print(f"Failed: {stats['failed']} papers")
print(f"Skipped: {stats['skipped']} papers")
```

## Features

- **Automatic Folder Creation**: Creates download directory if it doesn't exist
- **Smart Filenames**: Uses paper titles to create meaningful filenames
- **Duplicate Prevention**: Skips already downloaded papers
- **Source Support**: 
  - arXiv (automatic PDF URL conversion)
  - Direct PDF links (CrossRef, etc.)
  - Download status tracking
- **Retry Logic**: Automatically retries failed downloads up to 3 times
- **Progress Tracking**: Real-time download progress with file sizes
- **Error Handling**: Graceful handling of blocked, missing, or corrupted PDFs
- **Excel Integration**: Optional download status column in Excel output

## Command-Line Options

### download_papers.py

```
positional arguments:
  file                  Excel file with paper data

optional arguments:
  -h, --help           show this help message and exit
  --dir, -d DIR        Download directory (default: papers)
  --max, -m MAX        Maximum papers to download
  --update-excel       Save updated Excel with download status
```

### CLI download command

```
positional arguments:
  None

required arguments:
  -f, --file FILE      Input Excel file with paper data

optional arguments:
  -d, --dir DIR        Download directory (default: papers)
  -m, --max MAX        Maximum papers to download
  --update-excel       Save updated Excel with download status
```

## Output Structure

After downloading, your folder will look like:

```
papers/
├── A deep learning survey on natural language processing.pdf
├── Machine learning fundamentals and applications.pdf
├── Neural networks for computer vision.pdf
├── Attention is all you need.pdf
├── BERT pre-training of deep bidirectional transformers.pdf
└── ...
```

## Download Status

If you use `--update-excel` flag, the original Excel file will be saved with a new name including download status:

**Original file:** `papers.xlsx`
**Updated file:** `papers_with_downloads.xlsx`

The updated file includes a new "Downloaded" column showing:
- `Yes` - Successfully downloaded
- `No` - Failed or skipped

## Supported Sources

| Source | Link Format | Status |
|--------|------------|--------|
| arXiv | `https://arxiv.org/abs/...` or `https://arxiv.org/pdf/...` | ✅ Full Support |
| CrossRef/DOI | Direct PDF URLs | ✅ Full Support |
| Semantic Scholar | Links: `semanticscholar.org/...` | ⚠️ Limited (requires external access) |
| Direct URLs | Any PDF URL | ✅ Full Support |

## Troubleshooting

### No papers downloaded
- Check Excel file has `Link` column with valid URLs
- Verify internet connection
- Check file permissions in target directory

### Some papers fail to download
- These are likely protected behind paywalls
- Check download status in updated Excel file
- Papers from arXiv should work reliably

### Downloaded file is not a PDF
- Some servers return HTML pages instead of PDFs (access restrictions)
- The tool will auto-detect and skip these

### File not found error
- Make sure Excel file path is correct
- Use absolute path if file is in different directory: `C:\Users\...\papers.xlsx`

## Tips & Best Practices

1. **Start Small**: Test with `--max 5` before downloading 100+ papers
2. **Schedule Downloads**: Large batches may take time, run overnight
3. **Backup Results**: Use `--update-excel` to save progress
4. **Check Bandwidth**: Some papers are large (>10MB)
5. **Respect Servers**: The tool includes 1-second delays between downloads

## Examples

### Example 1: Download AI papers
```bash
# Search
python -m scholarly.cli search -q "artificial intelligence" -n 100 -o ai_papers.xlsx

# Download with limit
python download_papers.py ai_papers.xlsx --max 25

# Check papers in directory
dir papers/
```

### Example 2: Archive old search
```bash
# Download to organized folder
python download_papers.py my_old_search.xlsx --dir archive_2024_q1 --update-excel

# All papers saved to archive_2024_q1/ with status in updated Excel file
```

### Example 3: Python workflow
```python
from scholarly.cli import download_papers
from pathlib import Path

# Download with custom logic
download_papers(
    excel_file="papers.xlsx",
    download_dir="research_archive",
    max_downloads=50,
    update_excel=True
)

# Check results
papers_dir = Path("research_archive")
print(f"Downloaded {len(list(papers_dir.glob('*.pdf')))} papers")
```

## Requirements

All dependencies are already included in `requirements.txt`:
- pandas (for Excel handling)
- requests (for HTTP downloads)
- openpyxl (for Excel file format)

## Performance Notes

- **Download Speed**: Depends on server and file sizes (typically 1-100MB per paper)
- **Typical Rates**: 5-15 papers per minute with network latency
- **Retries**: Failed downloads retry up to 3 times automatically
- **Throttling**: 1-second delay between downloads to be respectful to servers

## Support

For issues or feature requests, please check:
1. Excel file has required columns (Title, Link)
2. URLs are valid and accessible
3. Sufficient disk space available
4. Internet connection is stable
