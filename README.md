# ScamShield

ScamShield checks a suspicious message or web link and tells you, in plain words, whether it looks like a **scam**, an **advertisement**, or a **normal message**, and what to do next. It works in **English, Bangla (বাংলা) and Banglish** (Bangla typed in English letters), and it was built with Bangladeshi scams in mind (fake bKash, Nagad, Robi and Daraz messages, prize traps, "your account will be closed" links).

Its helper, **Cyber**, is a friendly robot who explains the result, can read it aloud, and wanders around the web page while you use it.

> **ScamShield is a helper, not a guarantee.** It can be wrong in both directions. When money, passwords or OTPs are involved, confirm through the official app or hotline. Never share an OTP or PIN, whatever the message says.

## What it does

**Reads the message.** A small machine-learning model looks at the text (patterns of 2 to 5 letters, so spelling variations still count) and decides between three labels: *legit*, *promo*, *suspicious*.

**Checks the links.** Every link in the message gets its own checks:

| Check | What it looks for |
| --- | --- |
| Look-alike names | A link that imitates bKash, Nagad, Robi, Grameenphone, Daraz or Pathao but is not their real site |
| Risky endings and pressure words | Domain endings often used in scams, words like "verify now" or "claim" |
| Chat-app and IP-address links | Links that should not appear in a normal SMS |
| Short links | Treated as a weak signal only, because honest promos use them too |
| Short-link expansion (optional) | Asks only the short-link service where the link points. It never opens the website behind it |
| Domain age (optional) | A website registered a few weeks ago is more suspicious (looked up via RDAP) |
| Google Safe Browsing (optional) | Off by default. Needs your own free API key |
| Dial codes | Warns about codes like `*247#` that can move money from your phone |

**Gives a safety-first verdict.** The message score and the link score are combined so that doubt leans towards caution:
- Suspicious if the model is at least 50% sure it is a scam.
- "Be careful" between 30% and 50%.
- "Looks normal" or "Looks like an ad" only when the model is at least 50% sure of that.
- Otherwise "Cyber is not sure".
- A risky link raises the warning level. A Google Safe Browsing hit forces "scam".

**Explains itself.** Cyber's sentences are written from the facts the engine found (verdict, confidence, link findings, warning signs). Cyber never decides anything on its own. The page also shows which words pushed the result towards scam or safe, and marks them in your own message.

**Speaks.** A Listen button reads Cyber's answer using your browser's built-in voice. Nothing is uploaded for this. Bangla voice quality depends on the device (Microsoft Edge and Chrome usually have one).

**Comes in two forms.**
- A **website** (this repository's `web/` folder), served by the API.
- A **browser extension** (`extension/`, Edge and Chrome) that checks the current website, checks pasted or selected text, checks a right-clicked link, and can optionally warn you about risky sites as you browse.

## What it does not do

- **It cannot prove a message is genuine.** A real bKash cash-in notice and a forged copy have identical text. Telling them apart needs the sender, which a browser cannot see. This is a main reason for the planned Android app.
- **It cannot open and read a website's content.** It judges the address, not the page. A scam on a clean-looking, old or hacked domain can be missed.
- **It is not a virus scanner or a firewall.** It does not block, delete or report anything. It advises.
- **It has no blind accuracy test yet** (see Numbers). Treat every percentage as a development figure, not a promise.
- **It does not read your SMS.** There is no Android app yet.
- **Banglish spelling is a weak spot.** People spell the same Bangla word many ways. Spellings the model has not seen can slip through.
- **The Banglish training text is synthetic** (made from Bangla by a transliteration script), so its scores are optimistic.
- **Link rules are hand-weighted guesses**, and the list of official brand domains must be verified against each company's own materials before anyone relies on it.
- **Domain age is only a hint.** New honest sites exist, old sites get hacked, and some endings (such as `.bd`) may have no age data.
- **Google Safe Browsing is free for non-commercial use only**, and its results must carry the credit "Advisory provided by Google".
- **It is not ready for the public internet.** The API has simple rate limiting, but no accounts, no HTTPS setup and no abuse monitoring.

## Numbers (development figures, handle with care)

- Held-out message test (template rows excluded): English 0.970, Bangla 0.968, Banglish 0.967 (Banglish optimistic because it is synthetic).
- A 51-message "reality" set from real phone messages: the model gave a confident answer on 47 and was right 94% of the time. With the safety-first rule, none of 21 scams was called safe, and 1 of 16 genuine messages was a false alarm (a genuine-looking cash-in notice). **All 51 were used while building the rules, so this is not a blind test.**
- A blind hold-out set of real messages has not been built yet. Until it is, no accuracy claim is final.

## How it fits together

```
message or link
      |
      v
engine.py  ---- model.joblib (text model)
   |       ---- linkcheck.py, expand.py, domainage.py, reputation.py
   v
api.py (FastAPI)   /check   /check-url   /health
   |
   +--> web/index.html   (website with Cyber)
   +--> extension/       (Edge / Chrome)
   +--> (planned) Android app
```

Key files:

| File | Job |
| --- | --- |
| `engine.py` | Runs the text model and link checks and combines them into one verdict |
| `cyber.py` | Writes Cyber's explanation in English, Bangla and Banglish |
| `reasons_i18n.py` | Translates link findings into Bangla and Banglish |
| `api.py` | The web API, with a per-visitor rate limit |
| `linkcheck.py`, `expand.py`, `domainage.py`, `reputation.py` | The link checks |
| `run_all.py` | Rebuilds the dataset and retrains the model, step by step |
| `web/index.html` | The website |
| `extension/` | The browser extension |

## Run it yourself (Windows, PowerShell)

```powershell
cd E:\Projects\ScamShield
.\venv\Scripts\Activate.ps1
uvicorn api:app --reload
```

Open http://127.0.0.1:8000/ for the website. `/docs` shows the API. The model file (`model.joblib`) and the datasets are not stored in this repository. Create them with `python run_all.py` after placing the datasets in `data/`.

To install the extension: open `edge://extensions` (or `chrome://extensions`), turn on Developer mode, choose **Load unpacked**, and pick the `extension` folder. The API must be running.

Optional Google Safe Browsing: set the environment variable `SAFE_BROWSING_KEY` to your own key. Without it that check is simply skipped.

## Privacy

- Messages are checked on your own computer. Nothing is sent anywhere unless you tick **Look deeper at short links** (which contacts the short-link service) or enable Safe Browsing or domain-age lookups.
- The browser extension sends only a site's address up to the `?` (never the part after it) to your own local server, and only when you press a button or switch on the warning option.
- Voice uses your browser's built-in speech, not an online service.

## Roadmap

1. Build a blind hold-out set of real messages (names, numbers and accounts replaced with fake ones), then score the text model once without tuning.
2. Retrain the final model on all data and verify the brand domain list.
3. Android app with consent-based SMS reading, which also gives the sender name, and an on-device model so messages never leave the phone.
4. Hosted version with HTTPS, proper rate limiting and abuse protection.

## Credits and data licences

- **UCI SMS Spam Collection**, CC BY 4.0.
- **Mishra and Soni (2022) smishing dataset**: no licence listed. The authors are credited here, and the licence must be resolved before the data is shared.
- **Bangalabarta** Bangla scam dataset: licence field blank. Must be resolved before publishing.
- **PhiUSIIL phishing URL dataset**, CC BY 4.0, credit to its authors. (Used for an experiment that is not part of the current app.)
- **Google Safe Browsing**: "Advisory provided by Google." Free for non-commercial use only.
- Fonts: Bricolage Grotesque and Hind Siliguri, loaded from Google Fonts.
- Cyber the robot was designed for this project.

Datasets, trained models and real messages are deliberately excluded from this repository (see `.gitignore`) because several licences are unresolved and real messages are private.

## Licence

No code licence has been chosen yet.
