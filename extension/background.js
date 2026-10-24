// Runs in the background. Three jobs: (1) warn about risky sites while you browse (if switched on),
// (2) right-click "Check with Cyber" on selected text, (3) right-click a link to check it.
const API = "http://127.0.0.1:8000";
const cache = new Map();            // site address -> {time, result}, so we do not re-ask for 10 minutes
const TEN_MIN = 10 * 60 * 1000;

// Only the part before "?" is sent, so search words, tokens and ids in the address never leave the browser.
function cleanUrl(u) { const x = new URL(u); return x.origin + x.pathname; }

function worthChecking(u) {
  try {
    const x = new URL(u);
    if (x.protocol !== "http:" && x.protocol !== "https:") return false;      // skip chrome://, about:, files
    if (["localhost", "127.0.0.1"].includes(x.hostname)) return false;        // skip our own server
    return true;
  } catch { return false; }
}

async function checkUrl(url) {
  const key = cleanUrl(url), hit = cache.get(key);
  if (hit && Date.now() - hit.time < TEN_MIN) return hit.result;
  const r = await fetch(API + "/check-url", {
    method: "POST", headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url: key })
  });
  if (!r.ok) throw new Error("server " + r.status);
  const result = await r.json();
  cache.set(key, { time: Date.now(), result });
  return result;
}

function setBadge(tabId, level) {
  const look = { risky: ["!", "#E5383B"], check: ["?", "#F5A300"] }[level];
  if (!look) { chrome.action.setBadgeText({ tabId, text: "" }); return; }
  chrome.action.setBadgeText({ tabId, text: look[0] });
  chrome.action.setBadgeBackgroundColor({ tabId, color: look[1] });
}

// (1) automatic watching, off unless the person turns it on in the popup
chrome.tabs.onUpdated.addListener(async (tabId, change, tab) => {
  if (change.status !== "complete" || !worthChecking(tab.url)) return;
  const { auto } = await chrome.storage.local.get({ auto: false });
  if (!auto) return;
  try {
    const res = await checkUrl(tab.url);
    setBadge(tabId, res.level);
    if (res.level === "risky") notify("This website looks risky", "ScamShield: do not enter passwords, OTPs or money details here.");
  } catch { /* server not running: stay quiet */ }
});

function notify(title, message) {
  chrome.notifications.create({ type: "basic", iconUrl: "icon128.png", title, message });
}

// (2) and (3) right-click menu
chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.create({ id: "sel", title: "Check this text with Cyber", contexts: ["selection"] });
  chrome.contextMenus.create({ id: "lnk", title: "Check this link with Cyber", contexts: ["link"] });
});

chrome.contextMenus.onClicked.addListener(async (info) => {
  try {
    if (info.menuItemId === "sel") {
      const r = await fetch(API + "/check", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: info.selectionText.slice(0, 5000), lang: "en" })
      });
      const d = await r.json();
      notify("Cyber: " + d.verdict, (d.cyber && d.cyber.text || "").split("\n")[0]);
    } else {
      const res = await checkUrl(info.linkUrl);
      const words = { risky: "This link looks risky", check: "Be careful with this link", ok: "Nothing suspicious found in this link", unknown: "Cyber could not judge this link" };
      notify(words[res.level] || "Link checked", (res.reasons[0] || "A clean result is not a guarantee."));
    }
  } catch { notify("ScamShield", "Could not reach the ScamShield server. Is it running?"); }
});
