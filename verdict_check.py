import pandas as pd

df = pd.read_csv("reality_results.csv")


def verdict(row):
    if row["p_suspicious"] >= 0.5:
        return "suspicious"
    if row["p_suspicious"] >= 0.3:
        return "careful"
    best = "legit" if row["p_legit"] >= row["p_promo"] else "promo"
    if row["p_" + best] >= 0.5:
        return best
    return "not sure"


df["verdict"] = df.apply(verdict, axis=1)
print(pd.crosstab(df["expected"], df["verdict"]))