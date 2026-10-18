import random
import string

import pandas as pd

BN_DIGITS = str.maketrans("0123456789", "০১২৩৪৫৬৭৮৯")
ROWS_PER_FORMAT = 6


def phone(r):
    return "01" + r.choice("3456789") + "".join(r.choice(string.digits) for _ in range(8))


def amt(r):
    return r.choice(["200", "500", "800", "1000", "1500", "2000", "3000", "5000", "10000"])


def bal(r):
    return f"{r.randint(20, 9000)}.{r.choice(['00', '25', '50', '75'])}"


def trx(r):
    return "".join(r.choice(string.ascii_uppercase + string.digits) for _ in range(9))


def code(r):
    return "".join(r.choice(string.digits) for _ in range(r.choice([4, 6])))


def order(r):
    return str(r.randint(1000, 99999))


def when(r):
    return (f"{r.randint(1, 28):02d}/{r.randint(1, 12):02d}/2026 "
            f"{r.randint(8, 22):02d}:{r.choice(['05', '15', '30', '45', '52'])}")


def fake_link(r):
    return (f"{r.choice(['pay', 'secure', 'verify', 'card', 'account', 'update'])}-"
            f"{r.choice(['check', 'confirm', 'update', 'portal', 'help'])}-"
            f"{r.choice(['bd', '24', 'now', 'online'])}."
            f"{r.choice(['top', 'xyz', 'icu', 'click'])}/"
            f"{r.choice(['login', 'pay', 'verify'])}")


COMMON = {"amt": amt, "phone": phone, "bal": bal, "trx": trx,
          "code": code, "order": order, "when": when, "link": fake_link}

EN_DAYS = ["Monday", "Tuesday", "Thursday", "Saturday"]
BNL_DAYS = ["Robibar", "Sombar", "Mongolbar", "Budhbar", "Brihospotibar", "Shonibar"]
BN_DAYS = ["রবিবার", "সোমবার", "মঙ্গলবার", "বৃহস্পতিবার", "শনিবার"]

# Brand and shop names shared by all genuine money notices, so the model sees
# the same names on both the legit side and the scam side.
MONEY = {"brand": ["bKash", "Nagad", "Rocket", "Upay"],
         "shop": ["Daraz", "Pathao", "Foodpanda", "Grameenphone", "Robi"]}

# (name, label, language tag, [text formats], extra slot values)
TEMPLATES = [
    # ---- pressure-only scams (suspicious) ----
    ("emergency_en", "suspicious", "en", [
        "Hi, this is your {rel}. I'm in trouble and my phone is broken. Please send {amt} to {phone} right now.",
        "{trouble} Your {rel} needs help urgently. Send {amt} to {phone} and don't tell anyone."],
     {"rel": ["son", "daughter", "brother", "sister", "nephew"],
      "trouble": ["There was an accident.", "I am at the hospital.", "I got arrested.", "I lost my wallet abroad."]}),
    ("emergency_bnl", "suspicious", "bn_latn", [
        "apnar {rel} bipode poreche. Jaldi {amt} taka {phone} number e pathan, kauke bolben na.",
        "Ami apnar {rel}, phone nosto hoye geche. Notun number {phone}. Ekhoni {amt} tk bkash korun, khub joruri."],
     {"rel": ["chele", "meye", "bhai", "bon", "vagna"]}),
    ("emergency_bn", "suspicious", "bn", [
        "আপনার {rel} বিপদে পড়েছে। এখনই {amt} টাকা {phone} নম্বরে পাঠান, কাউকে বলবেন না।",
        "আমি আপনার {rel}, ফোন হারিয়ে ফেলেছি। এটা আমার নতুন নম্বর {phone}। এখনই {amt} টাকা বিকাশ করুন।"],
     {"rel": ["ছেলে", "মেয়ে", "ভাই", "বোন", "ভাগ্নে"]}),
    ("newnumber_en", "suspicious", "en", [
        "Hi {parent}, I dropped my phone in water. This is my new number {phone}. Can you send {amt} to pay a bill? I will repay you tonight.",
        "Hello {parent}, it's me. New number {phone}, the old one is broken. Please transfer {amt} urgently."],
     {"parent": ["mum", "dad", "mom"]}),
    ("newnumber_bnl", "suspicious", "bn_latn", [
        "{parent}, amar phone nosto hoye geche. Eta notun number {phone}. Joruri bill dite hobe, {amt} tk bkash kore dao.",
        "{parent}, ami bolchi. Notun number {phone}. Ekhon {amt} tk pathaite parbe? Pore ferot dibo."],
     {"parent": ["Ma", "Baba"]}),
    ("newnumber_bn", "suspicious", "bn", [
        "{parent}, আমার ফোন নষ্ট হয়ে গেছে। এটা আমার নতুন নম্বর {phone}। জরুরি বিল দিতে হবে, {amt} টাকা বিকাশ করে দাও।",
        "{parent}, আমি বলছি। নতুন নম্বর {phone}। এখন {amt} টাকা পাঠাতে পারবে? পরে ফেরত দেব।"],
     {"parent": ["মা", "বাবা"]}),
    ("aid_en", "suspicious", "en", [
        "You qualify for government relief of {amt}. Send your national ID and mobile wallet number to {phone} to claim. Last date today.",
        "Official notice: {amt} aid approved for you. Reply with your ID number and wallet number within 24 hours or it will be cancelled."],
     {}),
    ("aid_bnl", "suspicious", "bn_latn", [
        "Sorkar theke apnar jonno {amt} taka sahajjo manjur hoyeche. NID number ar bkash number {phone} e pathan. Shesh tarikh ajke.",
        "Apni sorkari bhata pacchen. Pete apnar NID ar nagad number ekhoni pathan, na hole bondho hoye jabe."],
     {}),
    ("aid_bn", "suspicious", "bn", [
        "সরকারি সহায়তা হিসেবে আপনার জন্য {amt} টাকা অনুমোদিত হয়েছে। পেতে এনআইডি নম্বর ও বিকাশ নম্বর {phone} এ পাঠান। শেষ তারিখ আজ।",
        "আপনি সরকারি ভাতার জন্য নির্বাচিত হয়েছেন। এখনই আপনার এনআইডি ও নগদ নম্বর পাঠান, না হলে বাতিল হয়ে যাবে।"],
     {}),
    ("mistake_en", "suspicious", "en", [
        "I sent {amt} to your wallet by mistake. Please return it to {phone}, it is an emergency.",
        "Sorry, wrong transfer of {amt}. TrxID {trx}. Kindly send it back to {phone} immediately."],
     {}),
    ("mistake_bnl", "suspicious", "bn_latn", [
        "Vul kore apnar number e {amt} tk pathiye felsi. Doya kore {phone} e ferot din, khub joruri.",
        "Sorry bhai, vul kore {amt} tk send hoye gese. TrxID {trx}. Ekhoni ferot pathan {phone} e."],
     {}),
    ("mistake_bn", "suspicious", "bn", [
        "ভুল করে আপনার নম্বরে {amt} টাকা চলে গেছে। দয়া করে {phone} নম্বরে ফেরত দিন, খুব জরুরি।",
        "ভাই, ভুল করে {amt} টাকা সেন্ড হয়ে গেছে। TrxID {trx}। এখনই ফেরত পাঠান {phone} নম্বরে।"],
     {}),
    ("job_en", "suspicious", "en", [
        "We are hiring online assistants. Earn {amt} per day from home. No experience needed. Join our Telegram group now.",
        "Part-time job offer: {amt} daily for simple tasks. Message us on WhatsApp {phone} to start."],
     {}),
    ("job_bnl", "suspicious", "bn_latn", [
        "Ghore bose din e {amt} taka income korun. Kono experience lagbe na. Telegram group e join korun.",
        "Part time job offer: roj {amt} tk. WhatsApp e message din {phone}."],
     {}),
    ("job_bn", "suspicious", "bn", [
        "ঘরে বসে প্রতিদিন {amt} টাকা আয় করুন। কোনো অভিজ্ঞতা লাগবে না। এখনই টেলিগ্রাম গ্রুপে যোগ দিন।",
        "পার্ট টাইম কাজের সুযোগ: প্রতিদিন {amt} টাকা। হোয়াটসঅ্যাপে মেসেজ দিন {phone}।"],
     {}),
    ("closure_en", "suspicious", "en", [
        "Your mobile wallet will be closed today due to incomplete verification. Call {phone} immediately.",
        "Security alert: your account is suspended. Call our officer on {phone} now to restore access."],
     {}),
    ("closure_bnl", "suspicious", "bn_latn", [
        "Apnar bkash account ajke bondho hoye jabe, verification baki ache. Ekhoni {phone} e call korun.",
        "Security alert: apnar account suspend kora hoyeche. Officer er sathe kotha bolte {phone} e call korun."],
     {}),
    ("closure_bn", "suspicious", "bn", [
        "অসম্পূর্ণ ভেরিফিকেশনের কারণে আপনার মোবাইল ওয়ালেট আজ বন্ধ হয়ে যাবে। এখনই {phone} নম্বরে কল করুন।",
        "সিকিউরিটি অ্যালার্ট: আপনার অ্যাকাউন্ট স্থগিত করা হয়েছে। এখনই {phone} নম্বরে কল করে সচল করুন।"],
     {}),
    # ---- look-alikes of genuine notices that carry a demand (suspicious) ----
    ("failed_en", "suspicious", "en", [
        "Payment failed. Update your payment details within 24 hours to avoid suspension: {link}",
        "We could not process your last payment. Confirm your card details here: {link}"],
     {}),
    ("failed_bnl", "suspicious", "bn_latn", [
        "Apnar payment fail hoyeche. 24 ghontar moddhe details update korun: {link}",
        "Apnar card verify kora jacche na. Ekhane click kore confirm korun: {link}"],
     {}),
    ("failed_bn", "suspicious", "bn", [
        "আপনার পেমেন্ট ব্যর্থ হয়েছে। ২৪ ঘণ্টার মধ্যে তথ্য আপডেট করুন: {link}",
        "আপনার কার্ড ভেরিফাই করা যাচ্ছে না। এখানে ক্লিক করে নিশ্চিত করুন: {link}"],
     {}),
    # ---- genuine-style notices (legit) ----
    ("money_en", "legit", "en", [
        "You have received Tk {amt}.00 from {phone}. Fee Tk 0.00. Balance Tk {bal}. TrxID {trx} at {when}",
        "Cash Out Tk {amt}.00 to {phone} successful. Fee Tk {fee}. Balance Tk {bal}. TrxID {trx} at {when}",
        "Your {brand} account has been credited with Tk {amt}. Balance Tk {bal}. TrxID {trx}.",
        "Cash In Tk {amt}.00 successful. Fee Tk 0.00. Balance Tk {bal}. TrxID {trx}",
        "Payment of Tk {amt} to {shop} successful. Balance Tk {bal}. TrxID {trx}"],
     {"fee": ["9.25", "14.75", "18.50"], **MONEY}),
    ("money_bnl", "legit", "bn_latn", [
        "Apni {phone} theke {amt}.00 tk peyechen. Balance {bal} tk. TrxID {trx} at {when}",
        "Apnar {amt} tk Send Money {phone} e successful hoyeche. Fee 5.00 tk. Balance {bal} tk. TrxID {trx}",
        "Apnar {brand} account e {amt} tk cash in hoyeche. Balance {bal} tk. TrxID {trx}.",
        "{brand}: {amt} tk cash out successful hoyeche. Fee {fee} tk. Balance {bal} tk. TrxID {trx}",
        "Apni {shop} e {amt} tk payment korechen. Balance {bal} tk. TrxID {trx}",
        "Apnar number e {amt} tk mobile recharge successful hoyeche. Balance {bal} tk."],
     {"fee": ["9.25", "14.75", "18.50"], **MONEY}),
    ("money_bn", "legit", "bn", [
        "আপনি {phone} থেকে {amt}.00 টাকা পেয়েছেন। ব্যালেন্স {bal} টাকা। TrxID {trx}, {when}",
        "আপনার {amt}.00 টাকা সেন্ড মানি {phone} নম্বরে সফল হয়েছে। ফি ৫.০০ টাকা। ব্যালেন্স {bal} টাকা। TrxID {trx}",
        "আপনার {brand} অ্যাকাউন্টে {amt} টাকা ক্যাশ ইন হয়েছে। ব্যালেন্স {bal} টাকা। TrxID {trx}।",
        "{brand}: {amt} টাকা ক্যাশ আউট সফল হয়েছে। ফি {fee} টাকা। ব্যালেন্স {bal} টাকা। TrxID {trx}",
        "আপনি {shop} এ {amt} টাকা পেমেন্ট করেছেন। ব্যালেন্স {bal} টাকা। TrxID {trx}"],
     {"fee": ["9.25", "14.75", "18.50"], **MONEY}),
    ("code_en", "legit", "en", [
        "Your verification code is {code}. Do not share it with anyone.",
        "{code} is your login code. It expires in 5 minutes. Never share this code."],
     {}),
    ("code_bnl", "legit", "bn_latn", [
        "Apnar verification code {code}. Kauke share korben na.",
        "{code} apnar login code. 5 minute por expire hobe."],
     {}),
    ("code_bn", "legit", "bn", [
        "আপনার ভেরিফিকেশন কোড {code}। এটি কারো সাথে শেয়ার করবেন না।",
        "{code} আপনার লগইন কোড। ৫ মিনিট পর মেয়াদ শেষ হবে।"],
     {}),
    ("appointment_en", "legit", "en", [
        "Reminder: your appointment is on {day} at {time}. Reply C to confirm or X to cancel.",
        "Your booking is confirmed for {day} at {time}. Reply CANCEL to cancel."],
     {"day": EN_DAYS, "time": ["9:30 AM", "11:00 AM", "3:30 PM", "5:15 PM"]}),
    ("appointment_bnl", "legit", "bn_latn", [
        "Reminder: apnar appointment {day} {time} e. Confirm korte C, cancel korte X likhe reply korun.",
        "Apnar booking confirm hoyeche, {day} {time}. Cancel korte CANCEL likhe reply korun."],
     {"day": BNL_DAYS, "time": ["sokal 10 ta", "dupur 2 ta", "bikel 4 ta"]}),
    ("appointment_bn", "legit", "bn", [
        "অনুস্মারক: আপনার অ্যাপয়েন্টমেন্ট {day} {time}। নিশ্চিত করতে C, বাতিল করতে X লিখে রিপ্লাই দিন।",
        "আপনার বুকিং নিশ্চিত হয়েছে, {day} {time}। বাতিল করতে CANCEL লিখে রিপ্লাই দিন।"],
     {"day": BN_DAYS, "time": ["সকাল ১০টায়", "দুপুর ২টায়", "বিকাল ৪টায়"]}),
    ("order_en", "legit", "en", [
        "Your order #{order} has shipped and will arrive on {day}. Thank you for shopping with us.",
        "Order #{order} is out for delivery today. Please keep your phone nearby."],
     {"day": EN_DAYS}),
    ("order_bnl", "legit", "bn_latn", [
        "Apnar order #{order} pathano hoyeche, {day} pouchabe. Dhonnobad.",
        "Order #{order} ajke deliver hobe. Phone ta kache rakhben."],
     {"day": BNL_DAYS}),
    ("order_bn", "legit", "bn", [
        "আপনার অর্ডার #{order} পাঠানো হয়েছে, {day} পৌঁছাবে। ধন্যবাদ।",
        "অর্ডার #{order} আজ ডেলিভারি হবে। দয়া করে ফোন হাতের কাছে রাখুন।"],
     {"day": BN_DAYS}),
    ("bill_en", "legit", "en", [
        "Your electricity bill of Tk {amt} has been paid successfully. Receipt no. {order}. Thank you.",
        "Payment received: Tk {amt} for your internet bill. Receipt {order}. Thank you."],
     {}),
    ("bill_bnl", "legit", "bn_latn", [
        "Apnar bidyut bill {amt} tk successfully joma hoyeche. Receipt no. {order}. Dhonnobad.",
        "Apnar internet bill {amt} tk grohon kora hoyeche. Receipt {order}. Dhonnobad."],
     {}),
    ("bill_bn", "legit", "bn", [
        "আপনার বিদ্যুৎ বিল {amt} টাকা সফলভাবে জমা হয়েছে। রসিদ নং {order}। ধন্যবাদ।",
        "আপনার ইন্টারনেট বিল {amt} টাকা গ্রহণ করা হয়েছে। রসিদ {order}। ধন্যবাদ।"],
     {}),
]


def build(rng):
    rows = []
    for name, label, language, formats, extra in TEMPLATES:
        slots = {**COMMON, **extra}
        for fmt in formats:
            for _ in range(ROWS_PER_FORMAT):
                values = {k: (v(rng) if callable(v) else rng.choice(v))
                          for k, v in slots.items()}
                text = fmt.format(**values)
                if language == "bn" and "TrxID" not in text and rng.random() < 0.5:
                    text = text.translate(BN_DIGITS)
                rows.append({
                    "label_raw": "template", "text": text, "language": language,
                    "source": "template", "label": label, "has_link": False,
                    "group_text": f"tpl:{name}",
                })
    return pd.DataFrame(rows)


df = pd.read_csv("merged_aug.csv")
df = df[df["source"] != "template"]
new = build(random.Random(11))
out = pd.concat([df, new], ignore_index=True)
out = out.drop_duplicates(subset="text").reset_index(drop=True)
out.to_csv("merged_aug.csv", index=False, encoding="utf-8-sig")

print(new.groupby(["language", "label"]).size())
print("Wrote merged_aug.csv with", len(out), "rows")