import re
import unicodedata


def normalize(text):
    text = re.sub(
        r"https?://\S+|www\.\S+|\b[\w-]+\.(?:com|net|org|info|xyz|top|bd|ly|me)\b\S*",
        "<URL>", text, flags=re.IGNORECASE,
    )
    text = re.sub(r"\+?\d[\d\s-]{5,}\d", "<PHONE>", text)
    text = re.sub(r"\d+", "<NUM>", text)
    return text.lower()

def clean_text(text):
    return unicodedata.normalize("NFC", text).lower()