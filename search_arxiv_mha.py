#!/usr/bin/env python3
"""Search arXiv directly for mental health apps papers."""

import requests
import xml.etree.ElementTree as ET

def search_arxiv_mental_health_apps(max_results=50):
    """Search arXiv for mental health apps papers."""
    
    url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": "all:(mental health apps)",
        "start": 0,
        "max_results": max_results
    }
    
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
            
            # Get PDF link
            link = ""
            for l in entry.findall('{http://www.w3.org/2005/Atom}link'):
                if l.attrib.get('type') == 'application/pdf':
                    link = l.attrib['href']
                    break
            if not link:
                # arXiv abstract link
                link = entry.find('{http://www.w3.org/2005/Atom}id').text
            
            items.append({
                "Topic": "mental health apps",
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

if __name__ == "__main__":
    print("\n🔍 Searching arXiv for 'mental health apps' papers...\n")
    results = search_arxiv_mental_health_apps(50)
    
    print(f"✅ Found {len(results)} papers on arXiv\n")
    
    for i, paper in enumerate(results, 1):
        print(f"{i}. {paper['Title']}")
        print(f"   Authors: {paper['Authors'][:70]}")
        print(f"   Year: {paper['Year']} | Source: {paper['Source']}")
        print()
    
    # Save to Excel
    import pandas as pd
    
    if results:
        df = pd.DataFrame(results)
        output_file = "mental_health_apps_arxiv.xlsx"
        df.to_excel(output_file, index=False)
        print(f"\n✅ Saved {len(results)} papers to {output_file}")
