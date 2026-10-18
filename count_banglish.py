import pandas as pd


def has_bangla(text):
    return any("\u0980" <= ch <= "\u09ff" for ch in text)


df = pd.read_csv("merged.csv")
bn = df[df["language"] == "bn"]
latin_only = bn[~bn["text"].apply(has_bangla)]

print("Bangla-tagged rows:", len(bn))
print("...with no Bangla letters at all:", len(latin_only))
print(latin_only.groupby("label_raw").size())