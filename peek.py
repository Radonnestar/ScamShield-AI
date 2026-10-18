import sys
from pathlib import Path

import pandas as pd

folder = Path(sys.argv[1])
lines = []
for path in sorted(folder.rglob("*")):
    if not path.is_file():
        continue
    lines.append(f"FILE: {path}  ({path.stat().st_size} bytes)")
    if path.suffix.lower() not in (".csv", ".tsv", ".txt"):
        continue
    try:
        try:
            df = pd.read_csv(path)
            enc = "utf-8"
        except UnicodeDecodeError:
            df = pd.read_csv(path, encoding="latin-1")
            enc = "latin-1"
        lines.append(f"  encoding: {enc}  shape: {df.shape}")
        lines.append(f"  columns: {list(df.columns)}")
        for col in df.columns:
            if df[col].nunique() <= 10:
                lines.append(f"  values of {col}: {df[col].value_counts().to_dict()}")
        lines.append(df.head(5).to_string())
    except Exception as e:
        lines.append(f"  could not read: {e}")

out = Path(f"peek_{folder.name}.txt")
out.write_text("\n".join(lines), encoding="utf-8")
print("Wrote", out)