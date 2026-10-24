"""Translate the link-check reasons (written in English in linkcheck.py) into Bangla / Banglish.

How it works: each rule is (keywords, bn_text, bnl_text). If ALL keywords appear in the
English reason (lower-cased), that rule's translation is used. If nothing matches we keep
the English reason and print it to the server console, so we can see which reasons still
need a translation and add a rule for them.
"""
import re

RULES = [
    (("look", "like"), "নামটি পরিচিত কোনো সেবার মতো দেখালেও এটি তাদের আসল সাইট নয়",
                       "Nam ta porichito kono sebar moto dekhale-o eta tader asol site noy"),
    (("lookalike",),   "নামটি পরিচিত কোনো সেবার মতো দেখালেও এটি তাদের আসল সাইট নয়",
                       "Nam ta porichito kono sebar moto dekhale-o eta tader asol site noy"),
    (("short",),       "এটি শর্ট লিংক, তাই আসল গন্তব্য লুকানো থাকে",
                       "Eta short link, tai asol gontobbo lukano thake"),
    (("chat",),        "চ্যাট অ্যাপের লিংক; এসএমএসে এমন লিংক সন্দেহজনক",
                       "Chat app-er link; SMS e emon link sondehojonok"),
    (("ip address",),  "ওয়েবসাইটের নামের জায়গায় সংখ্যার ঠিকানা আছে",
                       "Website-er namer jaygay shonkhyar thikana ache"),
    (("http",),        "সংযোগটি এনক্রিপ্টেড নয়",
                       "Songjog ta encrypted noy"),
]
# Rules that also need a number from the sentence (domain age).
AGE = re.compile(r"(\d+)\s*day")


def translate_reason(reason: str, lang: str) -> str:
    if lang == "en":
        return reason
    low = reason.lower()
    m = AGE.search(low)
    if m and ("old" in low or "age" in low or "new" in low):
        n = m.group(1)
        return (f"ডোমেইনটি মাত্র {n} দিন আগে তৈরি" if lang == "bn"
                else f"Domain ta matro {n} din age toiri")
    for words, bn, bnl in RULES:
        if all(w in low for w in words):
            return bn if lang == "bn" else bnl
    print("UNTRANSLATED REASON:", reason)   # shows up in the uvicorn window
    return reason
