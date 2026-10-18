import sys

import joblib

import urltext  # noqa: F401  (the saved model refers to urltext.clean_url)

model = joblib.load("url_model.joblib")

urls = sys.argv[1:] or [
    "https://myrobi.go.link/Elite",
    "cutt.ly/VyE697gS",
    "https://shorturl.at/Ewx4f",
    "bit.ly/4cM1aKK",
    "https://www.facebook.com/share/p/19g3cN5nbJ/",
    "https://www.bkash.com",
    "https://www.prothomalo.com",
    "bkash-verify-now.xyz/login",
    "secure-bankcheck.top/login",
    "nagad-kyc-update.top",
    "http://192.168.1.5/login",
]
for url, p in zip(urls, model.predict_proba(urls)[:, 1]):
    print(f"{p:5.2f}  {url}")