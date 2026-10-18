import http.client
from urllib.parse import urljoin, urlparse

from linkcheck import SHORTENERS, base_domain, check_one, level_of, split_host

REDIRECTS = (301, 302, 303, 307, 308)


def is_shortener(url):
    return base_domain(split_host(url)[2]) in SHORTENERS


def expand(url, max_hops=4):
    current = split_host(url)[0]
    for _ in range(max_hops):
        if not is_shortener(current):
            break
        conn = None
        try:
            parsed = urlparse(current)
            conn_class = (http.client.HTTPSConnection if parsed.scheme == "https"
                          else http.client.HTTPConnection)
            conn = conn_class(parsed.hostname, parsed.port, timeout=4)
            path = (parsed.path or "/") + (f"?{parsed.query}" if parsed.query else "")
            conn.request("GET", path, headers={
                "User-Agent": "Mozilla/5.0 (compatible; ScamShield-linkcheck/0.1)"})
            response = conn.getresponse()
            status, location = response.status, response.getheader("Location")
        except (OSError, http.client.HTTPException, ValueError):
            return {"final": current, "found": False}
        finally:
            if conn is not None:
                conn.close()
        if status in REDIRECTS and location:
            current = urljoin(current, location)
        else:
            break
    return {"final": current, "found": not is_shortener(current)}


def expand_links(links, limit=3):
    done = 0
    for link in links:
        if not is_shortener(link["url"]) or done >= limit:
            continue
        done += 1
        result = expand(link["url"])
        if not result["found"]:
            link["reasons"].append("Could not see where this link leads.")
            continue
        final = result["final"]
        score, reasons = check_one(final)
        link["destination"] = final
        link["score"] = score
        link["level"] = level_of(score)
        link["reasons"] = [f"Short link. It leads to {split_host(final)[2]}."] + reasons