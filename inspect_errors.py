import joblib
import pandas as pd
from sklearn.model_selection import StratifiedGroupKFold

from textutils import normalize

df = pd.read_csv("merged.csv")
df["group"] = df["text"].apply(normalize)

splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
_, test_idx = next(splitter.split(df["text"], df["label"], groups=df["group"]))
test = df.iloc[test_idx].copy()

model = joblib.load("model.joblib")
test["pred"] = model.predict(test["text"])

wrong = test[test["label"] != test["pred"]]
print(wrong.groupby(["language", "label_raw", "pred"]).size())

bn_wrong = wrong[wrong["language"] == "bn"]
bn_wrong[["label_raw", "pred", "text"]].to_csv(
    "bn_errors.csv", index=False, encoding="utf-8-sig"
)
print("Wrote bn_errors.csv")