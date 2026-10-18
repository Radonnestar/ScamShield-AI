import re

import joblib
import pandas as pd
import streamlit as st

import textutils  # noqa: F401  (the saved model refers to textutils.clean_text)
from domainage import add_age_signals, domain_age_days
from expand import expand_links
from linkcheck import DIAL_NOTE, analyze_links
from reputation import check_reputation

# Google's terms require this line, linked to its Safe Browsing Advisory page.
# I could not confirm that page's exact address: set it from the terms page.
ADVISORY_URL = "https://developers.google.com/safe-browsing/v4/usage-limits"

st.set_page_config(page_title="ScamShield", page_icon="🛡️")


@st.cache_resource
def load_model():
    return joblib.load("model.joblib")


@st.cache_data(ttl=300, show_spinner=False)
def reputation_for(urls):
    return check_reputation(list(urls))


@st.cache_data(ttl=3600, show_spinner=False)
def age_for(domain):
    return domain_age_days(domain)


model = load_model()
CLASSES = list(model.named_steps["clf"].classes_)
SUSP = CLASSES.index("suspicious")

EXAMPLES = {
    "(write your own)": "",
    "Made-up Banglish scam": "Apnar Nagad account suspend hoyeche. 24 ghontar moddhe update korun: nagad-kyc-help.top/verify",
    "Made-up English scam": "Your parcel could not be delivered. Pay a Tk 30 fee here to reschedule: parcel-fee-bd.xyz/pay",
    "Made-up Bangla scam": "আপনার বিকাশ অ্যাকাউন্ট আজ বন্ধ হয়ে যাবে। এখনই ভেরিফাই করুন: bkash-check-now.top/login",
    "Made-up payment notice": "You have received Tk 500.00 from 01712345678. Fee Tk 0.00. Balance Tk 1250.00. TrxID 8H4K2L9",
}

VERDICTS = {
    "suspicious": ("error", "🚨 Likely a scam",
                   "Do not click links, call numbers, or send money or codes."),
    "careful": ("warning", "⚠️ Be careful",
                "This message has warning signs. Check with the real company through its official app or number."),
    "legit": ("success", "✅ No warning signs found",
              "That is not a guarantee. Never share your PIN or one-time code."),
    "promo": ("info", "📣 Looks like advertising",
              "An offer or promotion, not necessarily a scam. Be careful with the links."),
    "not sure": ("info", "❓ ScamShield is not sure",
                 "The signals are mixed. Treat it with caution and check the sender another way."),
}

NOTICE_RE = re.compile(
    r"trxid|balance|cash[ -]?(?:in|out)|send money|ব্যালেন্স|ক্যাশ (?:ইন|আউট)|সেন্ড মানি",
    re.IGNORECASE,
)


def text_verdict(probs):
    p = dict(zip(CLASSES, probs))
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


def word_effects(text, max_words=80):
    words = text.split()[:max_words]
    if len(words) < 2:
        return []
    base = model.predict_proba([" ".join(words)])[0][SUSP]
    variants = [" ".join(words[:i] + words[i + 1:]) for i in range(len(words))]
    without = model.predict_proba(variants)[:, SUSP]
    return sorted(zip(words, base - without), key=lambda pair: pair[1])


st.title("🛡️ ScamShield")
st.write("Paste a message in English, Bangla or Banglish and see if it has the signs of a scam.")

example = st.selectbox("Try an example (all made up)", list(EXAMPLES))
text = st.text_area("Message", value=EXAMPLES[example], height=160)
look_up = st.checkbox("Look deeper: where short links lead and how old the site's domain is "
                      "(contacts the short-link service and public domain registries, never the site itself)")

if st.button("Check message", type="primary"):
    text = text.strip()[:2000]
    if not text:
        st.warning("Paste a message first.")
        st.stop()

    probs = model.predict_proba([text])[0]
    links = analyze_links(text)
    if look_up:
        expand_links(links["links"])
        add_age_signals(links["links"], lookup=age_for)
        links["worst"] = max((l["score"] for l in links["links"]), default=0.0)
    rep = reputation_for(tuple(link["url"] for link in links["links"]))
    base = text_verdict(probs)
    verdict = final_verdict(base, links["worst"], bool(rep["flagged"]))

    kind, title, advice = VERDICTS[verdict]
    getattr(st, kind)(f"**{title}**\n\n{advice}")

    if verdict != base:
        st.write("The links in this message raised the warning level.")
    if NOTICE_RE.search(text):
        st.info("This looks like a payment notice. Check your balance in the official bKash, "
                "Nagad or bank app. Never trust a link or phone number inside the message itself.")

    st.subheader("How sure is the model?")
    st.bar_chart(pd.Series(probs, index=CLASSES))

    if links["links"] or links["dial_codes"]:
        st.subheader("Links and dial codes")
        icons = {"ok": "⚪", "check": "🟡", "risky": "🔴"}
        for link in links["links"]:
            st.write(f"{icons[link['level']]} `{link['url']}`")
            for reason in link["reasons"]:
                st.caption(f"• {reason}")
        if links["links"]:
            st.caption("⚪ means no warning signs were found by our checks. It is not a guarantee.")
            if rep["status"] == "checked" and rep["flagged"]:
                for url, kinds in rep["flagged"].items():
                    st.warning(f"Google Safe Browsing lists `{url}` as a {', '.join(kinds)}.")
                st.caption(f"[Advisory provided by Google]({ADVISORY_URL}) · "
                           "[Learn about phishing](https://www.antiphishing.org/)")
            elif rep["status"] == "checked":
                st.caption("Not on Google's known-threat lists. That is no guarantee: brand-new scam "
                           "sites are not listed yet. Links (not the message) are sent to Google "
                           "Safe Browsing for this check.")
            elif rep["status"] == "error":
                st.caption("Could not reach the threat-list service, so that check was skipped.")
            else:
                st.caption("Threat-list check is off (no API key set).")
        for code in links["dial_codes"]:
            st.write(f"📞 `{code}`")
        if links["dial_codes"]:
            st.caption(DIAL_NOTE)

    effects = word_effects(text)
    up = [(w, e) for w, e in reversed(effects) if e >= 0.02][:5]
    down = [(w, e) for w, e in effects if e <= -0.02][:3]
    if up or down:
        st.subheader("Which words mattered")
        for word, effect in up:
            st.write(f"**{word}** raised the scam score by {effect * 100:.0f} points")
        for word, effect in down:
            st.write(f"**{word}** lowered it by {-effect * 100:.0f} points")

st.caption("ScamShield is a helper, not a guarantee. It can miss scams (false negatives) and "
           "sometimes flags genuine messages (false positives). It does not save the messages you paste.")