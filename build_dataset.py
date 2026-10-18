import re
import unicodedata
from pathlib import Path

import pandas as pd

from label_rules import apply_rules

# 1. English: UCI SMS Spam Collection
uci = pd.read_csv(
    "data/uci/SMSSpamCollection",
    sep="\t", header=None, names=["label_raw", "text"], quoting=3,
)
uci["language"] = "en"
uci["source"] = "uci"

# 2. English: Mishra & Soni (2022)
mishra = pd.read_csv("data/mishra/Dataset_5971.csv")
mishra = mishra.rename(columns={"LABEL": "label_raw", "TEXT": "text"})
mishra = mishra[["label_raw", "text"]].copy()
mishra["label_raw"] = "m_" + mishra["label_raw"].str.strip().str.lower()
mishra["language"] = "en"
mishra["source"] = "mishra"

# 3. Bangla
bn = pd.read_csv(next(Path("data/bangla").glob("*.csv")))
bn = bn.rename(columns={"label": "label_raw"})
bn["language"] = "bn"
bn["source"] = "bangalabarta"

# 4. Stack them (UCI first, so UCI's copy wins when a message appears twice)
df = pd.concat([mishra, uci, bn], ignore_index=True)
df["label_raw"] = df["label_raw"].str.strip().str.lower()

# 5. Map the different label names onto three shared labels
LABEL_MAP = {
    "ham": "legit",
    "normal": "legit",
    "promo": "promo",
    "spam": "suspicious",
    "smish": "suspicious",
    "m_ham": "legit",
    "m_spam": "promo",
    "m_smishing": "suspicious",
}
unmapped = set(df["label_raw"]) - set(LABEL_MAP)
if unmapped:
    raise SystemExit(f"Unknown labels, add them to LABEL_MAP: {unmapped}")
df["label"] = df["label_raw"].map(LABEL_MAP)

# 6. Clean: remove damaged characters, trim, standardize Unicode, drop duplicates
df["text"] = (
    df["text"].astype(str)
    .str.replace("\ufffd", "", regex=False)
    .str.strip()
    .apply(lambda t: unicodedata.normalize("NFC", t))
)
df = df[df["text"] != ""].reset_index(drop=True)

dup = df.duplicated(subset="text")
print("duplicates removed, by source:")
print(df[dup].groupby("source").size())
df = df[~dup].reset_index(drop=True)

# 7. Apply the label corrections
df = apply_rules(df)

# 8. Mark which messages contain a link
LINK_RE = re.compile(
    r"(?:https?://|www\.|\b[\w-]+\.(?:com|net|org|info|xyz|top|bd|ly|me)\b)",
    re.IGNORECASE,
)
df["has_link"] = df["text"].str.contains(LINK_RE)

# 9. Report, then save
print(df.groupby(["language", "label"]).size())
print(df.groupby(["language", "label_raw"])["has_link"].mean().round(2))
df.to_csv("merged.csv", index=False, encoding="utf-8-sig")
print("Saved merged.csv with", len(df), "rows")