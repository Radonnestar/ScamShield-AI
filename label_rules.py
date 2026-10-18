import unicodedata

RULES = [
    # (name, regex pattern, new label, only change rows currently labeled this; None = any)
    ("family emergency money request",
     r"(?s)আপনার\s*(?:ছেলে|মেয়ে|বাবা|মা|ভাই|বোন|স্বামী|স্ত্রী)"
     r".{0,40}?(?:বিপদে|হাসপাতালে|সমস্যায়|দুর্ঘটনা).{0,60}?টাকা",
     "suspicious", None),
    ("one-time codes are transactional",
     r"is your verification code|^<#>|শেয়ার করবেন না", "legit", "promo"),
    ("call charge notices are transactional",
     r"call duration.{0,40}remaining balance", "legit", "promo"),
    ("debit notice that only says call us",
     r"(?s)একাউন্ট থেকে.{0,25}টাকা.{0,25}(?:কাটা|প্রদান).{0,40}কল করুন",
     "suspicious", "legit"),
    ("urgent payment demand with no sender",
     r"(?:জলদি|দ্রুত|জরুরি)[^।]{0,25}(?:পরিশোধ|পরিষোধ)"
     r"|(?:পাওনা|বিল|পেমেন্ট)\s*(?:বাকি|রয়েছে)[^।]{0,40}(?:জলদি|দ্রুত|জরুরি)",
     "drop", "legit"),
    ("ambiguous templated notices",
     r"আপনার\s*(?:গাড়ির সার্ভিসিং|প্যাকেজের ডেলিভারি)|আমার একাউন্টে ৫০ হাজার",
     "drop", "legit"),
    ("garbled machine-made sentences",
     r"মেজবান পাখি|আমি একটি বিশেষ লোক হিসাবে|এই যা কোন অন্য জন্য|বিদ্যুতের চালার"
     r"|বিশেষ স্থান রেখে আসতে|পরিবার নির্মাণের|পারবারিক কাজের"
     r"|ব্রাউন করতে গিয়েছি|প্রাণ চলার জন্য",
     "drop", None),
    ("college admission greetings",
     r"মাধ্যমিক পরীক্ষায় উত্তীর্ণ", "promo", "suspicious"),
    ("unverifiable job notices",
     r"post name:", "drop", "suspicious"),
    ("travel package adverts",
     r"ভ্রমণ প্যাকেজে", "promo", None),
    ("operator and subscription offers",
     r"গ্রামীণফোন রিচার্জে|হেলথ প্লাসের", "promo", "suspicious"),
    ("english joke subscriptions",
     r"do you ever notice|do you realize that in about|divorce barbie"
     r"|how come it takes so little time|police station toilet stolen|arsenal dartboard",
     "drop", "suspicious"),
    ("english warnings and personal messages",
     r"scammers getting smart|allow companies to bill for sms"
     r"|been chasing us since sept|dating:i have had two",
     "legit", "suspicious"),
    ("english fragments",
     r"2/2 146tf150p|brought to you by gmw", "drop", None),
    ("english plain adverts",
     r"burger king - wanna play footy|xmas & new years eve tickets"
     r"|wrc rally in oz|areyouunique",
     "drop", "suspicious"),
    ("english messages that are really adverts",
     r"career tel|fullonsms\.com|customer service cum accounts executive",
     "drop", "legit"),
]


def apply_rules(df):
    for name, pattern, fix, only_if in RULES:
        pattern = unicodedata.normalize("NFC", pattern)
        hit = df["text"].str.contains(pattern, regex=True, case=False)
        if only_if is not None:
            hit &= (df["label"] == only_if)
        print(f"{hit.sum():4d} rows -> {fix:10s} {name}")
        df.loc[hit, "label"] = fix
    return df[df["label"] != "drop"].reset_index(drop=True)