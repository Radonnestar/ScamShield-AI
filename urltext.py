import re


def clean_url(url):
    url = url.strip().lower()
    url = re.sub(r"^[a-z][a-z0-9+.-]*://", "", url)
    url = re.sub(r"^www\d*\.", "", url)
    return re.split(r"[/?#]", url, maxsplit=1)[0]