import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import Pipeline

from linkcheck import base_domain, split_host
from urltext import clean_url

PATH = "data/phiusil/PhiUSIIL_Phishing_URL_Dataset.csv"

header = pd.read_csv(PATH, nrows=0).columns
url_col = next((c for c in header if c.lower() == "url"), None)
label_col = next((c for c in header if c.lower() == "label"), None)
if url_col is None or label_col is None:
    raise SystemExit(f"Could not find the URL and label columns. Columns are: {list(header)}")

df = pd.read_csv(PATH, usecols=[url_col, label_col])
df = df.rename(columns={url_col: "url", label_col: "label"})
df["url"] = df["url"].astype(str)
df = df.drop_duplicates(subset="url").reset_index(drop=True)
df["phish"] = (df["label"] == 0).astype(int)  # in this dataset 0 = phishing
print(df["phish"].value_counts().rename({0: "legit", 1: "phishing"}))

df["group"] = df["url"].apply(lambda u: base_domain(split_host(u)[2]))

splitter = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
train_idx, test_idx = next(splitter.split(df, df["phish"], groups=df["group"]))
train, test = df.iloc[train_idx], df.iloc[test_idx]

model = Pipeline([
    ("tfidf", TfidfVectorizer(analyzer="char", ngram_range=(3, 5), min_df=5,
                              preprocessor=clean_url, sublinear_tf=True)),
    ("clf", LogisticRegression(solver="liblinear", C=2.0)),
])
model.fit(train["url"], train["phish"])

print(classification_report(test["phish"], model.predict(test["url"]),
                            target_names=["legit", "phishing"], digits=3))

names = model.named_steps["tfidf"].get_feature_names_out()
order = model.named_steps["clf"].coef_[0].argsort()
print("Most phishing-like fragments:", [names[i] for i in order[::-1][:25]])
print("Most legit-like fragments:", [names[i] for i in order[:25]])

joblib.dump(model, "url_model.joblib")
print("Saved url_model.joblib")