#!/usr/bin/env python3
"""Check download status."""

import pandas as pd

try:
    df = pd.read_excel('mental_health_apps_with_downloads.xlsx')
    print(f"Total papers: {len(df)}")
    print(f"Downloaded: {len(df[df['Downloaded'] == 'Yes'])}")
    print(f"Failed/Skipped: {len(df[df['Downloaded'] == 'No'])}")
except FileNotFoundError:
    print("mental_health_apps_with_downloads.xlsx not found yet - download still in progress")
