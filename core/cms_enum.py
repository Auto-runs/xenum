# core/cms_enum.py
import requests
import os
import json
from colorama import Fore, Style

SIGNATURES = {
    "WordPress": {
        "keywords": ["wp-content", "wp-includes"],
        "headers": ["x-powered-by"],
        "files": ["/wp-login.php", "/xmlrpc.php"]
    },
    "Joomla": {
        "keywords": ["joomla"],
        "headers": ["set-cookie"],
        "files": ["/administrator/"]
    },
    "Drupal": {
        "keywords": ["drupal"],
        "headers": ["x-generator"],
        "files": ["/core/CHANGELOG.txt"]
    },
    "Magento": {
        "keywords": ["magento", "mage-"],
        "headers": [],
        "files": ["/RELEASE_NOTES.txt"]
    },
    "Shopify": {
        "keywords": ["cdn.shopify.com"],
        "headers": [],
        "files": []
    }
}

def run(target, output_file="results/cms_enum.json"):
    """
    CMS Enumeration: deteksi CMS populer via HTML, headers, dan file unik.
    """
    result = {
        "Module": "CMS Enumeration",
        "Target": target,
        "CMS": "Unknown",
        "Evidence": []
    }

    try:
        if not target.startswith(("http://", "https://")):
            url = f"http://{target}"
        else:
            url = target

        r = requests.get(url, timeout=8, allow_redirects=True)
        html = r.text.lower()
        headers = {k.lower(): v.lower() for k, v in r.headers.items()}

        for cms, sig in SIGNATURES.items():
            found = False

            # cek keywords di HTML
            for kw in sig["keywords"]:
                if kw in html:
                    result["CMS"] = cms
                    result["Evidence"].append(f"Keyword: {kw}")
                    found = True

            # cek headers
            for h in sig["headers"]:
                if h in headers and cms.lower() in headers[h]:
                    result["CMS"] = cms
                    result["Evidence"].append(f"Header: {h}={headers[h]}")
                    found = True

            # cek file unik
            for f in sig["files"]:
                try:
                    test_url = url.rstrip("/") + f
                    rf = requests.get(test_url, timeout=5, allow_redirects=True)
                    if rf.status_code == 200:
                        result["CMS"] = cms
                        result["Evidence"].append(f"File: {test_url}")
                        found = True
                except requests.RequestException:
                    continue

            if found:
                break  # langsung stop kalau sudah match

    except Exception as e:
        result["Error"] = str(e)

    # save hasil
    os.makedirs("results", exist_ok=True)
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        except json.JSONDecodeError:
            old_data = []
    else:
        old_data = []

    old_data.append(result)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(old_data, f, indent=2, ensure_ascii=False)

    if result["CMS"] != "Unknown":
        print(f"{Fore.GREEN}[+] CMS terdeteksi: {result['CMS']}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[-] CMS tidak terdeteksi{Style.RESET_ALL}")

    return result
