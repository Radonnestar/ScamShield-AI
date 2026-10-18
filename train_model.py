import joblib
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline

from textutils import clean_text, normalize

DOUBT_CUTOFF = 0.10


def make_model(class_weight=None):
    return Pipeline([
        ("tfidf", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2, preprocessor=clean_text)),
        ("clf", LogisticRegression(max_iter=1000, class_weight=class_weight)),
    ])


df = pd.read_csv("merged_aug.csv")
df["group"] = df["group_text"].apply(normalize)

splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
train_idx, test_idx = next(
    splitter.split(df["text"], df["label"], groups=df["group"])
)
train, test = df.iloc[train_idx].copy(), df.iloc[test_idx].copy()
test = test[test["source"] != "template"].copy()

# 1. Drop training rows whose label the model strongly disagrees with
inner = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=0)
probs = cross_val_predict(
    make_model("balanced"), train["text"], train["label"],
    groups=train["group"], cv=inner, method="predict_proba",
)
classes = sorted(train["label"].unique())
given = train["label"].map({c: i for i, c in enumerate(classes)}).to_numpy()
doubtful = probs[np.arange(len(train)), given] < DOUBT_CUTOFF
doubtful = doubtful & (train["source"].to_numpy() != "template")
print("Dropped from training as doubtful:", int(doubtful.sum()))
print(train[doubtful].groupby(["language", "label"]).size())
train = train[~doubtful]

# 2. Weights: every (language, label) group counts equally within its language
lang_size = train.groupby("language")["text"].transform("size")
pair_size = train.groupby(["language", "label"])["text"].transform("size")
n_labels = train.groupby("language")["label"].transform("nunique")
weights = lang_size / (n_labels * pair_size)

# 3. Train, then judge on the untouched test part
model = make_model()
model.fit(train["text"], train["label"], clf__sample_weight=weights)
test["pred"] = model.predict(test["text"])

print("=== ALL ===")
print(classification_report(test["label"], test["pred"], digits=3))
for lang in ["en", "bn", "bn_latn"]:
    part = test[test["language"] == lang]
    print(f"=== {lang} ({len(part)} test messages) ===")
    print(classification_report(part["label"], part["pred"], digits=3))

joblib.dump(model, "model.joblib")
print("Saved model.joblib")