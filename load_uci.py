import pandas as pd

df = pd.read_csv(
    "data/uci/SMSSpamCollection",
    sep="\t",
    header=None,
    names=["label", "text"],
    quoting=3,
)

print(df.shape)
print(df["label"].value_counts())
print("duplicate messages:", df.duplicated(subset="text").sum())