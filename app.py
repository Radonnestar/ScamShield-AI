import json

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from cyber import explain
from engine import analyze

# Google's terms require this line, linked to its Safe Browsing Advisory page.
# I could not confirm that page's exact address: set it from the terms page.
ADVISORY_URL = "https://developers.google.com/safe-browsing/v4/usage-limits"

st.set_page_config(page_title="ScamShield", page_icon="🛡️")

EXAMPLES = {
    "(write your own)": "",
    "Made-up Banglish scam": "Apnar Nagad account suspend hoyeche. 24 ghontar moddhe update korun: nagad-kyc-help.top/verify",
    "Made-up English scam": "Your parcel could not be delivered. Pay a Tk 30 fee here to reschedule: parcel-fee-bd.xyz/pay",
    "Made-up Bangla scam": "আপনার বিকাশ অ্যাকাউন্ট আজ বন্ধ হয়ে যাবে। এখনই ভেরিফাই করুন: bkash-check-now.top/login",
    "Made-up payment notice": "You have received Tk 500.00 from 01712345678. Fee Tk 0.00. Balance Tk 1250.00. TrxID 8H4K2L9",
}

VERDICTS = {
    "suspicious": ("error", "🚨 Likely a scam"),
    "careful": ("warning", "⚠️ Be careful"),
    "legit": ("success", "✅ No warning signs found"),
    "promo": ("info", "📣 Looks like advertising"),
    "not sure": ("info", "❓ ScamShield is not sure"),
}

LANGS = {"English": "en", "বাংলা": "bn", "Banglish": "bnl"}


def speak_button(text, lang_code):
    components.html(
        f"""
        <button onclick="speak()" style="padding:8px 14px;border-radius:8px;border:1px solid #888;
                cursor:pointer;font-size:15px;">🔊 Listen to Cyber</button>
        <script>
        function speak() {{
          const u = new SpeechSynthesisUtterance({json.dumps(text)});
          u.lang = {json.dumps(lang_code)};
          window.speechSynthesis.cancel();
          window.speechSynthesis.speak(u);
        }}
        </script>
        """,
        height=55,
    )


st.title("🛡️ ScamShield")
st.write("Paste a message in English, Bangla or Banglish and see if it has the signs of a scam.")

example = st.selectbox("Try an example (all made up)", list(EXAMPLES))
text = st.text_area("Message", value=EXAMPLES[example], height=160)
look_deeper = st.checkbox("Look deeper: where short links lead and how old the site's domain is "
                          "(contacts the short-link service and public domain registries, never the site itself)")
lang_label = st.radio("Cyber speaks", list(LANGS), horizontal=True)

if st.button("Check message", type="primary"):
    if not text.strip():
        st.warning("Paste a message first.")
        st.stop()

    result = analyze(text, look_deeper)

    kind, title = VERDICTS[result["verdict"]]
    getattr(st, kind)(f"**{title}**")

    cyber = explain(result, LANGS[lang_label])
    st.subheader("🤖 Cyber says")
    st.write(cyber["text"])
    speak_button(cyber["speech_text"], cyber["speech_lang"])

    if result["verdict"] != result["text_verdict"]:
        st.write("The links in this message raised the warning level.")

    st.subheader("How sure is the model?")
    st.bar_chart(pd.Series(result["probabilities"]))

    if result["links"] or result["dial_codes"]:
        st.subheader("Links and dial codes")
        icons = {"ok": "⚪", "check": "🟡", "risky": "🔴"}
        for link in result["links"]:
            st.write(f"{icons[link['level']]} `{link['url']}`")
            for reason in link["reasons"]:
                st.caption(f"• {reason}")
        if result["links"]:
            threat = result["threat_list"]
            st.caption("⚪ means no warning signs were found by our checks. It is not a guarantee.")
            if threat["status"] == "checked" and threat["flagged"]:
                for url, kinds in threat["flagged"].items():
                    st.warning(f"Google Safe Browsing lists `{url}` as a {', '.join(kinds)}.")
                st.caption(f"[Advisory provided by Google]({ADVISORY_URL}) · "
                           "[Learn about phishing](https://www.antiphishing.org/)")
            elif threat["status"] == "checked":
                st.caption("Not on Google's known-threat lists. That is no guarantee: brand-new scam "
                           "sites are not listed yet. Links (not the message) are sent to Google "
                           "Safe Browsing for this check.")
            elif threat["status"] == "error":
                st.caption("Could not reach the threat-list service, so that check was skipped.")
            else:
                st.caption("Threat-list check is off (no API key set).")
        for code in result["dial_codes"]:
            st.write(f"📞 `{code}`")
        if result["dial_codes"]:
            st.caption(result["dial_note"])

    if result["words_raising"] or result["words_lowering"]:
        st.subheader("Which words mattered")
        for item in result["words_raising"]:
            st.write(f"**{item['word']}** raised the scam score by {item['points']} points")
        for item in result["words_lowering"]:
            st.write(f"**{item['word']}** lowered it by {item['points']} points")

st.caption("ScamShield is a helper, not a guarantee. It can miss scams (false negatives) and "
           "sometimes flags genuine messages (false positives). It does not save the messages you paste.")