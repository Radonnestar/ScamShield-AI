import json
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone

from linkcheck import (BIG_PLATFORMS, BRANDS, CHAT_APPS, FORWARDERS, OFFICIAL_SUFFIXES,
                       SHORTENERS, base_domain, level_of, split_host)

NAME_RE = re.compile(r"[a-z0-9-]+(?:\.[a-z0-9-]+)+")

KNOWN = set(BIG_PLATFORMS) | set(SHORTENERS) | set(FORWARDERS) | set(CHAT_APPS)
for _words, _official in BRANDS.values():
    KNOWN |= _official


def domain_age_days(domain):
    if not NAME_RE.fullmatch(domain):
        return None
    request = urllib.request.Request(
        f"https://rdap.org/domain/{domain}",
        headers={"Accept": "application/rdap+json", "User-Agent": "ScamShield-linkcheck/0.1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.load(response)
    except (urllib.error.URLError, TimeoutError, ValueError):
        return None
    for event in data.get("events", []):
        if event.get("eventAction") == "registration":
            try:
                when = datetime.fromisoformat(event["eventDate"].replace("Z", "+00:00"))
            except (KeyError, ValueError):
                return None
            if when.tzinfo is None:
                when = when.replace(tzinfo=timezone.utc)
            return (datetime.now(timezone.utc) - when).days
    return None


def add_age_signals(links, lookup=domain_age_days, limit=3):
    done = 0
    for link in links:
        target = link.get("destination", link["url"])
        host = split_host(target)[2]
        if not host or host.endswith(OFFICIAL_SUFFIXES):
            continue
        base = base_domain(host)
        if base in KNOWN or done >= limit:
            continue
        done += 1
        days = lookup(base)
        if days is None:
            continue
        if days < 30:
            weight, note = 0.35, f"Domain {base} was registered only {days} days ago."
        elif days < 90:
            weight, note = 0.15, f"Domain {base} is fairly new ({days} days old)."
        else:
            continue
        link["score"] = round(1 - (1 - link["score"]) * (1 - weight), 2)
        link["level"] = level_of(link["score"])
        link["reasons"].append(note)