import random

import pandas as pd

from romanize import to_banglish


def has_bangla(text):
    return any("\u0980" <= ch <= "\u09ff" for ch in text)


df = pd.read_csv("merged.csv")
df["group_text"] = df["text"]

rng = random.Random(7)
bn = df[(df["language"] == "bn") & df["text"].apply(has_bangla)]

rows = []
for _, row in bn.iterrows():
    seen = set()
    for _ in range(2):
        text = to_banglish(row["text"], rng)
        if text in seen:
            continue
        seen.add(text)
        rows.append({**row.to_dict(), "text": text,
                     "language": "bn_latn", "source": "romanized"})

aug = pd.DataFrame(rows)
out = pd.concat([df, aug], ignore_index=True)
out.to_csv("merged_aug.csv", index=False, encoding="utf-8-sig")

preview = aug["text"].sample(20, random_state=1).str.replace("\n", " ")
with open("banglish_preview.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(preview))

print(out.groupby(["language", "label"]).size())
print("Wrote merged_aug.csv and banglish_preview.txt")