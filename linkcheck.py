import re
from urllib.parse import urlparse

URL_RE = re.compile(
    r"(?:https?://|www\.)[^\s<>\"']+"
    r"|\b(?:[a-z0-9-]+\.)+(?:com|net|org|info|xyz|top|icu|click|bd|ly|me|at|link|co|io|gl)\b"
    r"(?:/[^\s<>\"']*)?",
    re.IGNORECASE,
)
DIAL_RE = re.compile(r"\*[0-9০-৯]{1,4}(?:\*[0-9০-৯]+)*#")

TWO_LEVEL = {"com.bd", "gov.bd", "edu.bd", "org.bd", "net.bd", "ac.bd", "mil.bd", "co.uk"}
OFFICIAL_SUFFIXES = (".gov.bd", ".edu.bd", ".ac.bd", ".mil.bd")
SHORTENERS = {"bit.ly", "cutt.ly", "shorturl.at", "tinyurl.com", "t.co", "goo.gl", "is.gd",
              "rb.gy", "ow.ly", "tiny.cc", "t.ly", "rebrand.ly", "buff.ly", "s.id"}
FORWARDERS = {"go.link"}
CHAT_APPS = {"t.me", "wa.me", "telegram.me", "chat.whatsapp.com"}
BIG_PLATFORMS = {"facebook.com", "fb.com", "fb.me", "youtube.com", "youtu.be", "instagram.com"}
RISKY_TLDS = {"top", "xyz", "icu", "click", "buzz", "cfd", "sbs", "cyou", "monster", "rest",
              "vip", "loan", "work", "tk", "ml", "ga", "cf", "gq"}
ACTION_WORDS = ("login", "verify", "secure", "update", "confirm", "account",
                "password", "bonus", "prize", "claim", "otp")

# brand name -> (words that signal the brand, that brand's official domains).
# VERIFY each official domain against the company's own materials, and add more.
BRANDS = {
    "bKash": ({"bkash", "bikash"}, {"bkash.com"}),
    "Nagad": ({"nagad"}, {"nagad.com.bd"}),
    "Robi": ({"robi", "myrobi"}, {"robi.com.bd"}),
    "Grameenphone": ({"grameenphone"}, {"grameenphone.com"}),
    "Daraz": ({"daraz"}, {"daraz.com.bd"}),
    "Pathao": ({"pathao"}, {"pathao.com"}),
}

DIAL_NOTE = ("A dial code can buy a pack or start a paid subscription. "
             "Check the offer in the operator's app first.")


def split_host(url):
    if not re.match(r"[a-z][a-z0-9+.-]*://", url, re.IGNORECASE):
        url = "http://" + url
    try:
        parsed = urlparse(url)
        return url, parsed, (parsed.hostname or "").lower()
    except ValueError:
        return url, None, ""


def base_domain(host):
    parts = host.split(".")
    if len(parts) >= 3 and ".".join(parts[-2:]) in TWO_LEVEL:
        return ".".join(parts[-3:])
    return ".".join(parts[-2:])


def brand_lookalike(host, base):
    tokens = [t for t in re.split(r"[.\-_]", host) if t]
    for name, (words, official) in BRANDS.items():
        if base in official:
            continue
        for token in tokens:
            if any(token == w or (len(w) >= 5 and token.startswith(w)) for w in words):
                return name, sorted(official)[0]
    return None


def check_one(raw):
    url, parsed, host = split_host(raw)
    if parsed is None or not host:
        return 0.2, ["Could not read this link properly."]
    if host.endswith(OFFICIAL_SUFFIXES):
        return 0.0, ["Official Bangladesh government or education domain."]

    base = base_domain(host)
    tld = host.rsplit(".", 1)[-1]
    found = []  # (weight, reason)

    if base in SHORTENERS:
        found.append((0.20, "Short link: it hides where it really goes."))
    if base in FORWARDERS:
        found.append((0.15, "Forwarding link: the destination is not visible from the link."))
    if base in CHAT_APPS:
        found.append((0.15, "Moves you to a chat app. Scam offers often do this."))
    if base in BIG_PLATFORMS:
        found.append((0.05, "Well-known site, but anyone can post content there."))
    if tld in RISKY_TLDS:
        found.append((0.30, f"Ends in .{tld}, which is cheap and common in scam sites."))
    if re.fullmatch(r"\d{1,3}(\.\d{1,3}){3}", host):
        found.append((0.40, "Uses a raw number address instead of a name."))
    if "xn--" in host:
        found.append((0.30, "Uses look-alike characters in the name."))
    if "@" in parsed.netloc:
        found.append((0.40, "Contains '@', a trick to disguise the real address."))
    if base.split(".")[0].count("-") >= 2:
        found.append((0.15, "Name has several hyphens."))
    if len(host.split(".")) >= 5:
        found.append((0.15, "Unusually many sub-parts in the address."))
    if len(host) > 35:
        found.append((0.10, "Unusually long address."))
    if url.lower().startswith("http://") and raw.lower().startswith("http://"):
        found.append((0.10, "Not encrypted (http, not https)."))

    if base not in SHORTENERS | FORWARDERS | BIG_PLATFORMS:
        hit = brand_lookalike(host, base)
        if hit:
            found.append((0.35, f"Uses the name {hit[0]} but is not its official site "
                                f"({hit[1]}). Check in the official app."))

    where = (host + parsed.path).lower()
    hits = [w for w in ACTION_WORDS if w in where]
    if hits:
        found.append((0.20, f"Address contains pressure words: {', '.join(hits)}."))

    score = 1.0
    for weight, _ in found:
        score *= 1 - weight
    return round(1 - score, 2), [reason for _, reason in found]


def level_of(score):
    if score >= 0.4:
        return "risky"
    if score >= 0.15:
        return "check"
    return "ok"


def analyze_links(text):
    links = []
    for match in URL_RE.finditer(text):
        raw = match.group(0).rstrip(".,;:!?)\"'।")
        score, reasons = check_one(raw)
        links.append({"url": raw, "score": score, "level": level_of(score), "reasons": reasons})
    return {
        "links": links,
        "dial_codes": DIAL_RE.findall(text),
        "worst": max((l["score"] for l in links), default=0.0),
    }