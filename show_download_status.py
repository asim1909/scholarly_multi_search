#!/usr/bin/env python3
"""Show download status details."""

import pandas as pd

df = pd.read_excel('mental_health_apps_with_downloads.xlsx')

print(f"\n📊 DOWNLOAD STATUS SUMMARY\n")
print(f"Total papers: {len(df)}")
print(f"Downloaded: {len(df[df['Downloaded'] == 'Yes'])}")
print(f"Failed: {len(df[df['Downloaded'] == 'No'])}")

print(f"\n{'='*100}")
print("✅ SUCCESSFULLY DOWNLOADED:\n")
for idx, row in df[df['Downloaded'] == 'Yes'].iterrows():
    print(f"{idx+1}. {row['Title']}")

print(f"\n❌ FAILED/NOT DOWNLOADED (first 20):\n")
for idx, row in df[df['Downloaded'] == 'No'].head(20).iterrows():
    print(f"{idx+1}. {row['Title']}")
    print(f"   Link: {row['Link']}")
