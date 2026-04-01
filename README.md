# 📚 Scholarly Multi-Search

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive Python tool for discovering, aggregating, and exporting academic research papers from multiple sources. Search across CrossRef, arXiv, and Semantic Scholar simultaneously, with intelligent deduplication and Excel export capabilities.

## ✨ Features

- **Multi-Source Search**: Query CrossRef, arXiv, and Semantic Scholar in parallel
- **Smart Deduplication**: Automatic duplicate removal based on DOI and title matching  
- **Interactive CLI**: User-friendly prompts or command-line arguments
- **Excel Export**: Clean, structured output with comprehensive metadata
- **📥 Auto Paper Download**: Download research papers directly with organized file storage
- **PDF Extraction**: Extract titles and generate citation placeholders from local PDFs
- **Modular Design**: Clean package structure for easy extension

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone https://github.com/asim1909/scholarly-multi-search.git
cd scholarly-multi-search

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage
```bash
# Interactive mode (recommended for beginners)
python -m scholarly.cli

# Command-line mode
python -m scholarly.cli -q "machine learning" -n 100 -o ml_papers.xlsx

# Alternative entry point
python search_all_sources.py -q "artificial intelligence" -n 50
```

## 📁 Project Structure

```
scholarly-multi-search/
├── scholarly/                 # Main package
│   ├── __init__.py
│   ├── cli.py                # Command-line interface
│   ├── aggregator.py         # Deduplication logic
│   └── sources/              # Source adapters
│       ├── __init__.py
│       ├── crossref.py       # CrossRef API integration
│       ├── arxiv.py          # arXiv API integration
│       └── semanticscholar.py # Semantic Scholar API
├── search_all_sources.py     # Backward compatibility wrapper
├── extract_papers.py         # Local PDF processing
├── requirements.txt          # Python dependencies
└── README.md                 # This documentation
```

## 🛠️ Usage Examples

### Multi-Source Paper Search

**Interactive Mode:**
```bash
python -m scholarly.cli
# Follow the prompts for topic, result count, and output filename
```

**Command-Line Arguments:**
```bash
# Search for papers
python -m scholarly.cli search -q "deep learning" -n 75 -o deep_learning.xlsx

# Specific research area
python -m scholarly.cli search -q "quantum computing applications" -n 200 -o quantum_research.xlsx
```

**Available Flags:**
| Flag | Description | Default |
|------|-------------|---------|
| `-q, --query` | Research topic/keywords | *Required* |
| `-n, --num-results` | Results per source | 50 |
| `-o, --out` | Output filename | papers_all_sources.xlsx |

### 📥 Download Research Papers

After searching for papers, automatically download PDFs and organize them locally:

**Using Standalone Script (Recommended):**
```bash
# Download all papers from Excel file
python download_papers.py search_results.xlsx

# Download to custom folder
python download_papers.py search_results.xlsx --dir my_research_papers

# Download with limit and save download status
python download_papers.py search_results.xlsx --max 20 --update-excel
```

**Using CLI:**
```bash
# Download papers via CLI
python -m scholarly.cli download -f search_results.xlsx

# Custom folder and limits
python -m scholarly.cli download -f search_results.xlsx --dir papers_archive --max 30 --update-excel
```

**Download Flags:**
| Flag | Description | Default |
|------|-------------|---------|
| `-f, --file` | Excel file with paper data | *Required* |
| `-d, --dir` | Download directory | `papers` |
| `-m, --max` | Maximum papers to download | All |
| `--update-excel` | Save updated Excel with status | False |

**Features:**
- ✅ Automatic folder creation (`papers/` by default)
- ✅ Smart filename generation from paper titles
- ✅ Duplicate detection - skips already downloaded papers
- ✅ Handles arXiv, CrossRef, and direct PDF links
- ✅ Retry mechanism for failed downloads
- ✅ Progress tracking and detailed statistics
- ✅ Optional Excel status tracking

**Example Workflow:**
```bash
# 1. Search for papers
python -m scholarly.cli search -q "machine learning" -n 50 -o ml_papers.xlsx

# 2. Download papers to 'papers' folder
python download_papers.py ml_papers.xlsx

# 3. All papers saved to papers/ folder with organized names
# papers/
# ├── A survey of deep learning methods.pdf
# ├── Neural networks and learning systems.pdf
# └── ...
```

### Local PDF Processing

```bash
# Create a paper/ directory and place PDF files there
mkdir paper
cp /path/to/your/papers/*.pdf paper/

# Extract metadata
python extract_papers.py

# Output: papers.xlsx with Topic and APA columns
```

## 📊 Output Format

The generated Excel file contains the following columns:

| Column | Description | Example |
|--------|-------------|---------|
| **Topic** | Search query used | "machine learning" |
| **Title** | Paper title | "Attention Is All You Need" |
| **Authors** | Author list | "Vaswani, A., Shazeer, N., ..." |
| **Year** | Publication year | 2017 |
| **Abstract** | Paper abstract (when available) | "The dominant sequence transduction..." |
| **DOI** | Digital Object Identifier | "10.5555/3295222.3295349" |
| **Link** | Direct paper URL | "https://arxiv.org/abs/1706.03762" |
| **Source** | Origin database | "arXiv", "CrossRef", "SemanticScholar" |

## 🔧 Advanced Configuration

### Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.\.venv\Scripts\Activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### API Politeness
For heavy usage, consider:
- Adding delays between requests
- Setting a proper User-Agent header
- Respecting rate limits (especially for Semantic Scholar)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt pytest black flake8

# Run tests (when available)
pytest

# Format code
black scholarly/
```

## 📋 Roadmap

- [ ] CSV export option
- [ ] Year range filtering
- [ ] Abstract length limits
- [ ] Rate limiting configuration
- [ ] Additional sources (IEEE, PubMed)
- [ ] Citation format options (APA, MLA, Chicago)
- [ ] Batch processing capabilities

## 🐛 Troubleshooting

### Common Issues

**No results found:**
- Check internet connection
- Verify search terms are not too specific
- Try reducing the number of results requested

**SSL/Network errors:**
- Wait a few minutes and retry
- Check firewall settings
- Verify API endpoints are accessible

**Empty Excel file:**
- Ensure pandas and openpyxl are installed
- Check write permissions in output directory

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [CrossRef](https://www.crossref.org/) for bibliographic metadata
- [arXiv](https://arxiv.org/) for preprint access
- [Semantic Scholar](https://www.semanticscholar.org/) for AI-powered search
- Contributors and users of this project

---

**Made with ❤️ for researchers and academics worldwide**
- Topic (paper title)
- Year (publication year if available)
- Link (DOI URL)
- ScholarSearch (pre-built Google Scholar search URL for manual follow-up)

You can then choose which papers to download or inspect manually.

### Notes
- CrossRef relevance ranking is used.
- If you need abstracts or more metadata, we can extend the script.
- For >200 results, cursor-based pagination is used.

Ask if you’d like integration with arXiv, IEEE Xplore (requires API key), or automatic PDF download where permitted.
