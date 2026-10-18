from pathlib import Path

import joblib
import pandas as pd

model = joblib.load("model.joblib")
df = pd.concat(
    [pd.read_csv(p) for p in sorted(Path(".").glob("reality_check*.csv"))],
    ignore_index=True,
)

probs = model.predict_proba(df["text"])
for i, cls in enumerate(model.classes_):
    df[f"p_{cls}"] = probs[:, i].round(2)

df["pred"] = model.predict(df["text"])
df["correct"] = df["pred"] == df["expected"]

print(df.groupby("kind")["correct"].agg(["mean", "count"]).round(2))
wrong = df[~df["correct"]]
print(wrong[["kind", "expected", "pred", "p_legit", "p_promo", "p_suspicious"]])
df.to_csv("reality_results.csv", index=False, encoding="utf-8-sig")
df["conf"] = df[["p_legit", "p_promo", "p_suspicious"]].max(axis=1)
for cut in (0.5, 0.6, 0.7):
    sure = df[df["conf"] >= cut]
    print(f"confidence >= {cut}: answers {len(sure)} of {len(df)}, "
          f"correct {sure['correct'].mean():.2f}")
print("Wrote reality_results.csv")