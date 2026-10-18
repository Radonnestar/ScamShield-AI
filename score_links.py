from pathlib import Path

import pandas as pd

from linkcheck import DIAL_NOTE, analyze_links

df = pd.concat(
    [pd.read_csv(p) for p in sorted(Path(".").glob("reality_check*.csv"))],
    ignore_index=True,
)

for i, row in df.iterrows():
    result = analyze_links(row["text"])
    if not result["links"] and not result["dial_codes"]:
        continue
    print(f"[{i}] {row['kind']} / expected {row['expected']}")
    for link in result["links"]:
        print(f"   {link['level']:<6} {link['score']:.2f}  {link['url']}")
        for reason in link["reasons"]:
            print(f"          - {reason}")
    for code in result["dial_codes"]:
        print(f"   dial code {code}: {DIAL_NOTE}")