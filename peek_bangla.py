from pathlib import Path
import pandas as pd

lines = []
for path in sorted(Path("data/bangla").rglob("*")):
    if not path.is_file():
        continue
    lines.append(f"FILE: {path}  ({path.stat().st_size} bytes)")
    try:
        suffix = path.suffix.lower()
        if suffix == ".csv":
            df = pd.read_csv(path)
        elif suffix == ".json":
            df = pd.read_json(path)
        elif suffix in (".xlsx", ".xls"):
            df = pd.read_excel(path)
        else:
            continue
        lines.append(f"  shape: {df.shape}")
        lines.append(f"  columns: {list(df.columns)}")
        lines.append(df.head(5).to_string())
    except Exception as e:
        lines.append(f"  could not read: {e}")

Path("bangla_peek.txt").write_text("\n".join(lines), encoding="utf-8")
print("Wrote bangla_peek.txt")