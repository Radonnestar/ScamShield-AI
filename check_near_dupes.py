import re
from pathlib import Path
import pandas as pd

df = pd.read_csv("merged.csv")

def normalize(text):
    text = re.sub(
        r"https?://\S+|www\.\S+|\b[\w-]+\.(?:com|net|org|info|xyz|top|bd|ly|me)\b\S*",
        "<URL>", text, flags=re.IGNORECASE,
    )
    text = re.sub(r"\+?\d[\d\s-]{5,}\d", "<PHONE>", text)
    text = re.sub(r"\d+", "<NUM>", text)
    return text.lower()

df["norm"] = df["text"].apply(normalize)

print(df.groupby("language").size())
print(df.groupby("language")["norm"].nunique())

top = df["norm"].value_counts().head(10)
Path("templates.txt").write_text(top.to_string(), encoding="utf-8")
print("Wrote templates.txt")