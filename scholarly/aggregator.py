def deduplicate(rows):
    seen = set()
    out = []
    for row in rows:
        key = row.get("DOI") or (row.get("Title") or "").lower()
        if key and key not in seen:
            seen.add(key)
            out.append(row)
    return out
