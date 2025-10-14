import requests
import xml.etree.ElementTree as ET

def search_arxiv(query: str, max_results: int = 50):
    url = "http://export.arxiv.org/api/query"
    params = {"search_query": f"all:{query}", "start": 0, "max_results": max_results}
    items = []
    
    try:
        r = requests.get(url, params=params, timeout=20, headers={"User-Agent": "ScholarlyMultiSearch/0.1"})
        r.raise_for_status()
        root = ET.fromstring(r.text)
        
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            authors = ", ".join([a.find('{http://www.w3.org/2005/Atom}name').text for a in entry.findall('{http://www.w3.org/2005/Atom}author')])
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' ')
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip().replace('\n', ' ')
            year = None
            published = entry.find('{http://www.w3.org/2005/Atom}published').text
            if published:
                year = published[:4]
            link = ""
            for l in entry.findall('{http://www.w3.org/2005/Atom}link'):
                if l.attrib.get('type') == 'application/pdf':
                    link = l.attrib['href']
                    break
            if not link:
                link = entry.find('{http://www.w3.org/2005/Atom}id').text
            items.append({
                "Topic": query,
                "Title": title,
                "Authors": authors,
                "Year": year,
                "Abstract": summary,
                "DOI": "",
                "Link": link,
                "Source": "arXiv"
            })
    except Exception as e:
        print(f"arXiv search error: {e}")
        
    return items
