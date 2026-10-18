import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline

from textutils import normalize

df = pd.read_csv("merged.csv")
groups = df["text"].apply(normalize)

model = Pipeline([
    ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2)),
    ("clf", LogisticRegression(max_iter=1000, class_weight="balanced")),
])

cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
probs = cross_val_predict(
    model, df["text"], df["label"], groups=groups, cv=cv, method="predict_proba"
)

classes = sorted(df["label"].unique())
given = df["label"].map({c: i for i, c in enumerate(classes)}).to_numpy()
df["p_given"] = probs[np.arange(len(df)), given]

review = df.sort_values("p_given").head(150)[["language", "label", "text"]].copy()
review["fix"] = ""
review.to_csv("label_review.csv", index=False, encoding="utf-8-sig")
print("Wrote label_review.csv with", len(review), "rows")