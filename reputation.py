import json
import os
import urllib.error
import urllib.request

from linkcheck import split_host

ENDPOINT = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
THREAT_TYPES = ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"]
LABELS = {
    "SOCIAL_ENGINEERING": "possible phishing or deceptive site",
    "MALWARE": "possible malware site",
    "UNWANTED_SOFTWARE": "possible unwanted-software site",
    "POTENTIALLY_HARMFUL_APPLICATION": "possible harmful-app site",
}


def check_reputation(raw_urls):
    key = os.environ.get("SAFE_BROWSING_KEY")
    if not key:
        return {"status": "not_configured", "flagged": {}}

    urls = [split_host(u)[0] for u in raw_urls][:20]
    if not urls:
        return {"status": "checked", "flagged": {}}

    body = {
        "client": {"clientId": "scamshield", "clientVersion": "0.1"},
        "threatInfo": {
            "threatTypes": THREAT_TYPES,
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": u} for u in urls],
        },
    }
    request = urllib.request.Request(
        f"{ENDPOINT}?key={key}",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return {"status": "error", "flagged": {}}

    flagged = {}
    for match in data.get("matches", []):
        url = match["threat"]["url"]
        flagged.setdefault(url, []).append(LABELS.get(match["threatType"], "possible threat"))
    return {"status": "checked", "flagged": flagged}