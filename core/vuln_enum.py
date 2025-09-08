# core/vuln_enum.py
import requests
import re
import concurrent.futures
import os
import json
from datetime import datetime

requests.packages.urllib3.disable_warnings()

DEFAULT_CHECKS = {
    "phpinfo": "/phpinfo.php",
    "robots": "/robots.txt",
    "server_status": "/server-status",
    "passwd_traversal": "/../../../../etc/passwd",
    "env_file": "/.env",
    "git_repo": "/.git/config",
    "backup": "/backup.zip",
    "db_dump": "/db.sql",
    "admin_panel": "/admin/",
    "wp_config": "/wp-config.php",
    "ds_store": "/.DS_Store",
    "crossdomain": "/crossdomain.xml",
    "client_secrets": "/client_secrets.json"
}

SENSITIVE_PATTERNS = {
    "AWS Key": r"AKIA[0-9A-Z]{16}",
    "Private Key": r"-----BEGIN PRIVATE KEY-----",
    "API Key": r"(?i)(api[_-]?key|secret)[=:\"'\\s][A-Za-z0-9\\-_]{16,}",
    "Password": r"(?i)password[=:\"'\\s][^\\s<>]+"
}


def fetch_url(name, url, limit_snippet=200):
    try:
        resp = requests.get(url, timeout=6, verify=False, allow_redirects=True)
        result = None

        if resp.status_code == 200 and len(resp.text.strip()) > 0:
            snippet = re.sub(r"\s+", " ", resp.text[:limit_snippet])
            result = {
                "check": name,
                "url": url,
                "status": resp.status_code,
                "length": len(resp.text),
                "snippet": snippet
            }

            if "Index of /" in resp.text or "Directory listing" in resp.text:
                result["note"] = "Possible directory listing enabled"

            leaks = []
            for label, regex in SENSITIVE_PATTERNS.items():
                if re.search(regex, resp.text):
                    leaks.append(label)
            if leaks:
                result["leaks"] = leaks

        elif resp.status_code in [301, 302] and "login" in resp.headers.get("Location", "").lower():
            result = {
                "check": name,
                "url": url,
                "status": resp.status_code,
                "note": "Redirected to login page"
            }

        return result

    except requests.exceptions.RequestException:
        return None


def run(target, scheme="http", extra_paths=None, limit_snippet=200, threads=10, save=True):
    results = []
    base_url = f"{scheme}://{target}"

    checks = DEFAULT_CHECKS.copy()
    if extra_paths:
        checks.update(extra_paths)

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(fetch_url, name, base_url + path, limit_snippet): name
            for name, path in checks.items()
        }
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            if res:
                results.append(res)

    output = {
        "Module": "Vulnerability Enumeration",
        "Target": target,
        "Findings": results if results else "No obvious vulns detected ✅"
    }

    # Save hasil scan
    if save:
        os.makedirs("results", exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        txt_file = f"results/vuln_enum_{target.replace('.', '_')}_{ts}.txt"
        json_file = txt_file.replace(".txt", ".json")

        with open(txt_file, "w", encoding="utf-8") as f:
            f.write(json.dumps(output, indent=2))

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2)

        print(f"[+] Results saved to {txt_file} and {json_file}")

    return output
