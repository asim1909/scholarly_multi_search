import re
import requests

USER_AGENT = {"User-Agent": "ScholarlyMultiSearch/0.1 (mailto:example@example.com)"}

def search_crossref(query: str, max_results: int = 50):
    url = "https://api.crossref.org/works"
    params = {"query": query, "rows": min(max_results, 100), "sort": "relevance"}
    items = []
    cursor = None
    
    try:
        while len(items) < max_results:
            if cursor:
                params["cursor"] = cursor
            r = requests.get(url, params=params, headers=USER_AGENT, timeout=20)
            r.raise_for_status()
            data = r.json()
            for item in data["message"]["items"]:
                items.append({
                    "Topic": query,
                    "Title": item.get("title", [""])[0],
                    "Authors": ", ".join([f"{a.get('given', '')} {a.get('family', '')}" for a in item.get("author", [])]),
                    "Year": item.get("issued", {}).get("date-parts", [[None]])[0][0],
                    "Abstract": re.sub('<.*?>', '', item.get("abstract", "")),
                    "DOI": item.get("DOI", ""),
                    "Link": item.get("URL", ""),
                    "Source": "CrossRef"
                })
                if len(items) >= max_results:
                    break
            if "next-cursor" in data["message"]:
                cursor = data["message"]["next-cursor"]
            else:
                break
    except Exception as e:
        print(f"CrossRef search error: {e}")
        
    return items[:max_results]
