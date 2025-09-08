# core/http_enum.py
import requests
import hashlib
import ssl
import socket
from urllib.parse import urlparse

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

def get_ssl_info(host, port=443):
    """Ambil info SSL certificate"""
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(5)
            s.connect((host, port))
            cert = s.getpeercert()
            return {
                "subject": dict(x[0] for x in cert.get("subject", [])),
                "issuer": dict(x[0] for x in cert.get("issuer", [])),
                "valid_from": cert.get("notBefore"),
                "valid_until": cert.get("notAfter")
            }
    except Exception:
        return None


def run(target, scheme="http"):
    """
    HTTP Enumeration (enhanced):
    - Status code
    - Headers
    - Redirect chain
    - Page title
    - Body length + hash
    - SSL/TLS info (kalau HTTPS)
    - Basic fingerprint (server, waf, etc.)
    """
    results = {"Module": "HTTP Enumeration", "Target": target}
    url = f"{scheme}://{target}"

    try:
        # Follow redirects, simpan riwayat
        resp = requests.get(url, timeout=8, verify=False, allow_redirects=True)
        history = [r.url for r in resp.history] if resp.history else []

        results.update({
            "final_url": resp.url,
            "status_code": resp.status_code,
            "headers": dict(resp.headers),
            "redirect_chain": history,
            "body_length": len(resp.text),
            "body_md5": hashlib.md5(resp.content).hexdigest()
        })

        # Ambil title (case-insensitive)
        title = None
        text_lower = resp.text.lower()
        if "<title>" in text_lower:
            start = text_lower.find("<title>")
            end = text_lower.find("</title>", start)
            if start != -1 and end != -1:
                title = resp.text[start+7:end].strip()
        results["title"] = title if title else "N/A"

        # Basic fingerprint
        server = resp.headers.get("Server")
        powered_by = resp.headers.get("X-Powered-By")
        waf = None
        if "cloudflare" in (server or "").lower():
            waf = "Cloudflare"
        elif "sucuri" in (server or "").lower():
            waf = "Sucuri"
        results["fingerprint"] = {
            "server": server,
            "x_powered_by": powered_by,
            "waf": waf
        }

        # SSL info kalau HTTPS
        if scheme == "https":
            hostname = urlparse(url).hostname
            ssl_info = get_ssl_info(hostname)
            if ssl_info:
                results["ssl_certificate"] = ssl_info

    except requests.exceptions.RequestException as e:
        results["error"] = str(e)

    return results
