import requests
import time

API_URL = "https://api.semanticscholar.org/graph/v1/paper/search"

def search_semanticscholar(query: str, max_results: int = 50):
    params = {"query": query, "limit": max_results, "fields": "title,authors,year,abstract,externalIds,url"}
    
    # Try up to 3 times with exponential backoff
    for attempt in range(3):
        try:
            r = requests.get(API_URL, params=params, timeout=20, headers={"User-Agent": "ScholarlyMultiSearch/0.1"})
            r.raise_for_status()
            data = r.json()
            items = []
            for paper in data.get("data", []):
                authors = ", ".join([a.get("name", "") for a in paper.get("authors", [])])
                doi = paper.get("externalIds", {}).get("DOI", "")
                items.append({
                    "Topic": query,
                    "Title": paper.get("title", ""),
                    "Authors": authors,
                    "Year": paper.get("year", ""),
                    "Abstract": paper.get("abstract", ""),
                    "DOI": doi,
                    "Link": paper.get("url", ""),
                    "Source": "SemanticScholar"
                })
            return items
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:  # Rate limited
                wait_time = 2 ** attempt  # Exponential backoff: 1s, 2s, 4s
                print(f"Semantic Scholar rate limited. Waiting {wait_time}s... (attempt {attempt + 1}/3)")
                time.sleep(wait_time)
                continue
            else:
                print(f"Semantic Scholar error: {e}")
                break
        except Exception as e:
            print(f"Semantic Scholar connection error: {e}")
            break
    
    # Return empty list if all attempts failed
    print("Semantic Scholar search failed. Continuing with other sources.")
    return []
