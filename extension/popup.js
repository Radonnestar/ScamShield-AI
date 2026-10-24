const API = "http://127.0.0.1:8000";
const $ = id => document.getElementById(id);

// Draw a result box. textContent (not innerHTML) keeps text from the server from running as code.
function show(box, cls, title, lines) {
  box.hidden = false; box.className = "out " + cls; box.replaceChildren();
  const b = document.createElement("b"); b.textContent = title; box.append(b);
  if (lines.length) {
    const ul = document.createElement("ul");
    lines.forEach(t => { const li = document.createElement("li"); li.textContent = t; ul.append(li); });
    box.append(ul);
  }
}
async function post(path, body) {
  const r = await fetch(API + path, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  if (!r.ok) { const j = await r.json().catch(() => ({})); throw new Error(j.detail || "server " + r.status); }
  return r.json();
}
const offline = e => e instanceof TypeError ? "Could not reach the ScamShield server. Is it running?" : e.message;

$("page").onclick = async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  const box = $("pageOut");
  try {
    const u = new URL(tab.url);
    if (!/^https?:$/.test(u.protocol)) return show(box, "", "This page can't be checked.", ["Only normal web pages (http or https) can be checked."]);
    const res = await post("/check-url", { url: u.origin + u.pathname, lang: $("lang").value });
    const t = {
      risky: ["risky", "This website looks risky"], check: ["check", "Be careful on this website"],
      ok: ["ok", "Nothing suspicious found"], unknown: ["", "Cyber could not judge this address"]
    }[res.level] || ["", "Checked"];
    const lines = res.reasons.slice();
    if (res.level === "ok") lines.push("This is not a guarantee. Never share OTPs or passwords unless you started the action.");
    show(box, t[0], t[1], lines);
  } catch (e) { show(box, "risky", "Check failed", [offline(e)]); }
};

$("go").onclick = async () => {
  const text = $("msg").value.trim(), box = $("msgOut");
  if (!text) return show(box, "", "Paste a message first.", []);
  try {
    const d = await post("/check", { text, lang: $("lang").value });
    const cls = { suspicious: "risky", careful: "check", legit: "ok", promo: "promo" }[d.verdict] || "";
    show(box, cls, d.cyber.text.split("\n")[0], d.cyber.text.split("\n").slice(1));
  } catch (e) { show(box, "risky", "Check failed", [offline(e)]); }
};

// remember the settings
chrome.storage.local.get({ auto: false, lang: "en" }).then(s => { $("auto").checked = s.auto; $("lang").value = s.lang; });
$("auto").onchange = () => chrome.storage.local.set({ auto: $("auto").checked });
$("lang").onchange = () => chrome.storage.local.set({ lang: $("lang").value });
