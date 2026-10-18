import re
import unicodedata

HASANTA = "\u09cd"   # the mark that joins two consonants
NUKTA = "\u09bc"     # the dot under a letter

CONSONANTS = {
    "ক": ["k"], "খ": ["kh"], "গ": ["g"], "ঘ": ["gh"], "ঙ": ["ng"],
    "চ": ["ch", "c"], "ছ": ["ch", "chh"], "জ": ["j"], "ঝ": ["jh"], "ঞ": ["n"],
    "ট": ["t"], "ঠ": ["th"], "ড": ["d"], "ঢ": ["dh"], "ণ": ["n"],
    "ত": ["t"], "থ": ["th"], "দ": ["d"], "ধ": ["dh"], "ন": ["n"],
    "প": ["p"], "ফ": ["f", "ph"], "ব": ["b"], "ভ": ["v", "bh"], "ম": ["m"],
    "য": ["j", "z"], "র": ["r"], "ল": ["l"], "শ": ["sh", "s"], "ষ": ["sh", "s"],
    "স": ["s", "sh"], "হ": ["h"], "ৎ": ["t"],
}
NUKTA_FORMS = {"ড": ["r"], "ঢ": ["rh"], "য": ["y"]}
VOWELS = {
    "অ": ["o"], "আ": ["a"], "ই": ["i"], "ঈ": ["i", "ee"], "উ": ["u"],
    "ঊ": ["u", "oo"], "ঋ": ["ri"], "এ": ["e"], "ঐ": ["oi"], "ও": ["o"], "ঔ": ["ou"],
}
SIGNS = {
    "া": ["a"], "ি": ["i"], "ী": ["i", "ee"], "ু": ["u"], "ূ": ["u", "oo"],
    "ৃ": ["ri"], "ে": ["e"], "ৈ": ["oi"], "ো": ["o"], "ৌ": ["ou"],
}
OTHERS = {"ং": "ng", "ঃ": "", "ঁ": "", "৳": "tk ", HASANTA: "", NUKTA: ""}
DIGITS = str.maketrans("০১২৩৪৫৬৭৮৯", "0123456789")

RAW_WORDS = {
    "আপনার": ["apnar", "aponar", "apnr"], "আপনি": ["apni", "aponi"],
    "আপনাকে": ["apnake", "aponake"], "আমি": ["ami"], "তুমি": ["tumi"],
    "একাউন্ট": ["account", "acount"], "অ্যাকাউন্ট": ["account", "acount"],
    "অ্যাকাউন্টে": ["account e", "accounte"], "বিকাশ": ["bkash", "bikash"],
    "নগদ": ["nagad", "nogod"], "রকেট": ["rocket"], "ব্যাংক": ["bank", "byank"],
    "টাকা": ["taka", "tk"], "টাকার": ["takar", "tk er"],
    "নম্বর": ["number", "nombor"], "নম্বরে": ["number e", "nombore"],
    "নাম্বার": ["number", "nambar"], "নাম্বারে": ["number e", "nambare"],
    "পাঠান": ["pathan", "send korun"], "জলদি": ["joldi", "jaldi"],
    "দ্রুত": ["druto", "taratari"], "এখনই": ["ekhoni", "ekhuni"],
    "আজই": ["ajoi", "ajkei"], "বন্ধ": ["bondho", "bondh", "bandho"],
    "হয়েছে": ["hoyeche", "hoise", "hoyese"], "হবে": ["hobe"],
    "যাবে": ["jabe"], "করুন": ["korun", "koren"], "করতে": ["korte"],
    "করে": ["kore"], "যোগাযোগ": ["jogajog", "jogayog"], "ফি": ["fee", "fi"],
    "অফার": ["offer", "ofar"], "বোনাস": ["bonus", "bonas"], "লিংক": ["link"],
    "ক্লিক": ["click", "klik"], "ভেরিফাই": ["verify", "veriphy"],
    "আপডেট": ["update", "apdate"], "কল": ["call", "kol"],
    "জিতেছেন": ["jitechen", "jitesen"], "জিতুন": ["jitun"],
    "লটারি": ["lottery", "lotari"], "পুরস্কার": ["puroskar", "prize"],
    "ইনভেস্ট": ["invest"], "সরকার": ["sorkar", "government"],
    "সরকারী": ["sorkari", "sarkari"], "ভর্তুকি": ["bhortuki", "subsidy"],
    "ভিসা": ["visa"], "চাকরি": ["chakri", "job"], "বেতন": ["beton", "salary"],
    "কাজ": ["kaj"], "স্কিম": ["scheme", "skim"], "নির্বাচিত": ["nirbachito", "selected"],
    "ছেলে": ["chele", "chhele"], "মেয়ে": ["meye"], "বিপদে": ["bipode"],
    "হাসপাতালে": ["haspatale", "hospital e"], "ডিসকাউন্ট": ["discount", "diskaunt"],
    "সুযোগ": ["suyog", "chance"], "সমস্যা": ["somossa", "problem"],
    "সমস্যায়": ["somossay", "problem e"], "আছে": ["ache", "ase"],
    "এখানে": ["ekhane"], "পিন": ["pin"], "ওটিপি": ["otp"], "কোড": ["code"],
    "পাসওয়ার্ড": ["password", "pass"], "কার্ড": ["card"], "ব্লক": ["block"],
    "মোবাইল": ["mobile"], "ইন্টারনেট": ["internet", "net"], "রিচার্জ": ["recharge"],
    "প্যাকেজ": ["package"], "ডেলিভারি": ["delivery"], "লাভ": ["labh", "profit"],
    "ঘরে": ["ghore"], "বসে": ["boshe", "bose"], "ধন্যবাদ": ["dhonnobad", "thanks"],
    "ভাই": ["bhai", "vai"], "ভাইয়া": ["bhaiya", "vaiya"], "কি": ["ki"], "কী": ["ki"],
    "না": ["na"], "হ্যাঁ": ["ha", "hya"], "আজ": ["aj", "aaj"], "কাল": ["kal"],
    "দেখা": ["dekha"], "রাতে": ["rate"],
}
WORDS = {unicodedata.normalize("NFC", k): v for k, v in RAW_WORDS.items()}


def romanize_run(run, rng):
    run = unicodedata.normalize("NFC", run)
    if run in WORDS:
        return rng.choice(WORDS[run])
    out = []
    vowel_seen = False
    n = len(run)
    i = 0
    while i < n:
        ch = run[i]
        if ch in CONSONANTS:
            options = CONSONANTS[ch]
            if i + 1 < n and run[i + 1] == NUKTA:
                options = NUKTA_FORMS.get(ch, options)
                i += 1
            out.append(rng.choice(options))
            nxt = run[i + 1] if i + 1 < n else ""
            if nxt in SIGNS:
                pass
            elif nxt == HASANTA:
                i += 1
            elif i + 1 >= n:
                if rng.random() < 0.1:
                    out.append("o")
            elif not vowel_seen:
                out.append("o")
                vowel_seen = True
            elif rng.random() < 0.3:
                out.append("o")
        elif ch in VOWELS:
            out.append(rng.choice(VOWELS[ch]))
            vowel_seen = True
        elif ch in SIGNS:
            out.append(rng.choice(SIGNS[ch]))
            vowel_seen = True
        elif ch in OTHERS:
            out.append(OTHERS[ch])
        else:
            out.append(ch.translate(DIGITS))
        i += 1
    return "".join(out)


def to_banglish(text, rng):
    parts = re.split(r"([\u0980-\u09ff]+)", text)
    for k in range(1, len(parts), 2):
        parts[k] = romanize_run(parts[k], rng)
    return "".join(parts).replace("।", ".").lower()