import re
import time
from functools import wraps
from pathlib import Path

import joblib

import textutils  # noqa: F401  (the saved model refers to textutils.clean_text)
from domainage import add_age_signals, domain_age_days
from expand import expand_links
from linkcheck import DIAL_NOTE, analyze_links
from reputation import check_reputation

MODEL_PATH = Path(__file__).parent / "model.joblib"
MAX_CHARS = 2000

NOTICE_RE = re.compile(
    r"trxid|balance|cash[ -]?(?:in|out)|send money|ব্যালেন্স|ক্যাশ (?:ইন|আউট)|সেন্ড মানি",
    re.IGNORECASE,
)


def ttl_cache(seconds):
    def decorate(func):
        store = {}

        @wraps(func)
        def wrapper(*args):
            now = time.time()
            hit = store.get(args)
            if hit and now - hit[0] < seconds:
                return hit[1]
            value = func(*args)
            failed = value is None or (isinstance(value, dict) and value.get("status") == "error")
            if not failed:
                store[args] = (now, value)
            return value

        return wrapper

    return decorate


@ttl_cache(300)
def reputation_for(urls):
    return check_reputation(list(urls))


@ttl_cache(3600)
def age_for(domain):
    return domain_age_days(domain)


_model = None


def get_model():
    global _model
    if _model is None:
        _model = joblib.load(MODEL_PATH)
    return _model


def text_verdict(classes, probs):
    p = dict(zip(classes, probs))
    if p["suspicious"] >= 0.5:
        return "suspicious"
    if p["suspicious"] >= 0.3:
        return "careful"
    best = "legit" if p["legit"] >= p["promo"] else "promo"
    return best if p[best] >= 0.5 else "not sure"


def final_verdict(base, worst_link, known_bad):
    if known_bad:
        return "suspicious"
    if worst_link >= 0.4:
        if base == "careful":
            return "suspicious"
        if base != "suspicious":
            return "careful"
    return base


def word_effects(model, text, susp_index, max_words=80):
    words = text.split()[:max_words]
    if len(words) < 2:
        return []
    base = model.predict_proba([" ".join(words)])[0][susp_index]
    variants = [" ".join(words[:i] + words[i + 1:]) for i in range(len(words))]
    without = model.predict_proba(variants)[:, susp_index]
    return sorted(zip(words, base - without), key=lambda pair: pair[1])
def unique_top(pairs, limit):
    seen, out = set(), []
    for word, points in pairs:
        if word not in seen:
            seen.add(word)
            out.append({"word": word, "points": points})
        if len(out) == limit:
            break
    return out

def analyze(text, look_deeper=False):
    text = text.strip()[:MAX_CHARS]
    if not text:
        raise ValueError("The message is empty.")

    model = get_model()
    classes = list(model.named_steps["clf"].classes_)
    probs = model.predict_proba([text])[0]

    links = analyze_links(text)
    if look_deeper:
        expand_links(links["links"])
        add_age_signals(links["links"], lookup=age_for)
        links["worst"] = max((l["score"] for l in links["links"]), default=0.0)

    threat_list = reputation_for(tuple(link["url"] for link in links["links"]))
    base = text_verdict(classes, probs)
    verdict = final_verdict(base, links["worst"], bool(threat_list["flagged"]))

    effects = word_effects(model, text, classes.index("suspicious"))
    return {
        "verdict": verdict,
        "text_verdict": base,
        "probabilities": {c: float(p) for c, p in zip(classes, probs)},
        "links": links["links"],
        "dial_codes": links["dial_codes"],
        "dial_note": DIAL_NOTE,
        "threat_list": threat_list,
        "payment_notice": bool(NOTICE_RE.search(text)),
        "words_raising": unique_top(
            [(w, round(e * 100)) for w, e in reversed(effects) if e >= 0.02], 5),
        "words_lowering": unique_top(
            [(w, round(-e * 100)) for w, e in effects if e <= -0.02], 3),
    }