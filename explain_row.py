import sys

import joblib
import numpy as np
import pandas as pd

model = joblib.load("model.joblib")
tfidf = model.named_steps["tfidf"]
clf = model.named_steps["clf"]

df = pd.read_csv("reality_results.csv")
row = df.loc[int(sys.argv[1])]
print(row["text"])
print("expected:", row["expected"], "| predicted:", row["pred"])

vec = tfidf.transform([row["text"]])
names = tfidf.get_feature_names_out()
classes = list(clf.classes_)
wrong = classes.index(row["pred"])
right = classes.index(row["expected"])

contrib = vec.toarray()[0] * (clf.coef_[wrong] - clf.coef_[right])
for i in np.argsort(contrib)[::-1][:12]:
    print(repr(names[i]), round(contrib[i], 3))