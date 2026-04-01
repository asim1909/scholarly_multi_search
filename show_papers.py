#!/usr/bin/env python3
"""Display wearable mental health papers."""

import pandas as pd

df = pd.read_excel('wearable_mental_health.xlsx')

print("\n" + "="*110)
print("📊 WEARABLE DEVICES IN MENTAL HEALTH - RESEARCH PAPERS")
print("="*110)
print(f"\n✅ Total Papers Found: {len(df)}\n")

for idx, row in df.iterrows():
    print(f"[{idx + 1}] {row['Title']}")
    print(f"    📝 Authors: {row['Authors']}")
    print(f"    📅 Year: {row['Year']} | 🔗 Source: {row['Source']}")
    if pd.notna(row.get('DOI')) and row.get('DOI') != '':
        print(f"    🏷️  DOI: {row['DOI']}")
    print()

stats = df['Source'].value_counts()
print("="*110)
print(f"📈 Papers by Source:")
for source, count in stats.items():
    print(f"   • {source}: {count} papers")
print("="*110 + "\n")
