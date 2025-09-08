# core/wayback_enum.py
import requests
import os
import json
import re
import concurrent.futures
import time
from colorama import Fore, Style
from datetime import datetime
from urllib.parse import urlparse

WAYBACK_API = "https://web.archive.org/cdx/search/cdx"  # pakai HTTPS biar stabil

SENSITIVE_KEYWORDS = ["admin", "login", "backup", "config", "test", "db", "old"]

requests.packages.urllib3.disable_warnings()


def fetch_wayback_urls(domain, limit=200, filter_ext=None, filter_status=None, retries=3):
    """
    Ambil URL lama dari Internet Archive (Wayback Machine) dengan retry.
    """
    params = {
        "url": f"{domain}/*",
        "output": "json",
        "fl": "original,statuscode,timestamp",
        "collapse": "urlkey"
    }

    for attempt in range(1, retries + 1):
        try:
            r = requests.get(WAYBACK_API, params=params, timeout=60)
            r.raise_for_status()
            data = r.json()

            results = []
            for row in data[1:]:  # skip header
                url, status, timestamp = row

                if filter_status and status not in filter_status:
                    continue
                if filter_ext and not any(url.lower().endswith(f".{ext}") for ext in filter_ext):
                    continue

                has_params = "?" in url
                keywords = [k for k in SENSITIVE_KEYWORDS if k in url.lower()]

                results.append({
                    "url": url,
                    "status": status,
                    "timestamp": timestamp,
                    "has_params": has_params,
                    "keywords": keywords if keywords else None
                })

            return results[:limit]

        except Exception as e:
            print(f"{Fore.RED}[!] Error fetch_wayback_urls (attempt {attempt}/{retries}): {e}{Style.RESET_ALL}")
            if attempt < retries:
                print(f"{Fore.YELLOW}[*] Retry dalam 5 detik...{Style.RESET_ALL}")
                time.sleep(5)

    return []


def verify_live_url(base_domain, wayback_url, scheme="http"):
    """
    Cek apakah path dari Wayback masih hidup di target real.
    """
    try:
        parsed = urlparse(wayback_url)
        path = parsed.path
        if parsed.query:
            path += "?" + parsed.query

        real_url = f"{scheme}://{base_domain}{path}"
        resp = requests.get(real_url, timeout=6, verify=False, allow_redirects=True)

        return {
            "original_url": wayback_url,
            "real_url": real_url,
            "alive": resp.status_code < 400,
            "live_status": resp.status_code
        }
    except Exception:
        return {
            "original_url": wayback_url,
            "real_url": None,
            "alive": False
        }


def run(target, limit=20, filter_ext=None, filter_status=None, scheme="http",
        verify_live=True, threads=15, output_prefix="results/wayback_enum"):
    """
    Main function untuk enumerasi URL dari Wayback Machine + optional live verification.
    """
    print(f"{Fore.YELLOW}[*] Mengambil data Wayback untuk {target}{Style.RESET_ALL}")
    urls = fetch_wayback_urls(target, limit=limit, filter_ext=filter_ext, filter_status=filter_status)

    live_results = []
    if verify_live and urls:
        print(f"{Fore.CYAN}[*] Mengecek apakah URL masih hidup di {scheme}://{target}{Style.RESET_ALL}")
        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            futures = [executor.submit(verify_live_url, target, u["url"], scheme) for u in urls]
            for i, f in enumerate(concurrent.futures.as_completed(futures), 1):
                res = f.result()
                live_results.append(res)

                # progress bar di terminal
                status_color = Fore.GREEN if res["alive"] else Fore.RED
                print(f"{Fore.WHITE}[{i}/{len(urls)}] {res['original_url']} "
                      f"-> {status_color}{'Alive' if res['alive'] else 'Dead'}"
                      f"{Style.RESET_ALL}")

        # gabungkan data lama + hasil live check
        for u in urls:
            match = next((lr for lr in live_results if lr["original_url"] == u["url"]), None)
            if match:
                u.update({
                    "real_url": match["real_url"],
                    "alive": match["alive"],
                    "live_status": match.get("live_status")
                })

    # --- simpan hasil ---
    result = {
        "Module": "Wayback Machine Enumeration",
        "Target": target,
        "Total": len(urls),
        "Wayback_URLs": urls
    }

    os.makedirs("results", exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    json_file = f"{output_prefix}_{target.replace('.', '_')}_{ts}.json"
    txt_file = json_file.replace(".json", ".txt")

    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    with open(txt_file, "w", encoding="utf-8") as f:
        for u in urls:
            line = f"{u['url']} (archived {u['status']})"
            if verify_live:
                line += f" => {u.get('real_url')} [{'Alive' if u.get('alive') else 'Dead'}] "
            if u.get("keywords"):
                line += f"[Keywords: {','.join(u['keywords'])}]"
            f.write(line + "\n")

    print(f"{Fore.GREEN}[+] {len(urls)} URL ditemukan, hasil tersimpan di {json_file} & {txt_file}{Style.RESET_ALL}")
    return result
