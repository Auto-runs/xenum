# core/tech_detect_enum.py
import json
import os
import requests
from colorama import Fore, Style
from Wappalyzer import Wappalyzer, WebPage
from tabulate import tabulate
import urllib3

# disable SSL warning dari urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# pakai session biar efisien
session = requests.Session()
session.verify = False


def run(target: str, output_file: str = "results/tech_detect.jsonl"):
    """
    Deteksi teknologi pada target menggunakan Wappalyzer.
    - Bisa auto fallback http/https
    - Simpan hasil ke JSON Lines (lebih scalable daripada JSON array)
    - Tambah info server headers
    """
    if not target or len(target) < 3:
        print(f"{Fore.RED}[!] Target tidak valid{Style.RESET_ALL}")
        return None

    try:
        print(f"{Fore.YELLOW}[*] Memulai teknologi detection untuk: {target}{Style.RESET_ALL}")

        # coba dengan https dulu, fallback ke http
        urls_to_try = [f"https://{target}", f"http://{target}"] if not target.startswith("http") else [target]

        webpage, url_used = None, None
        for url in urls_to_try:
            try:
                webpage = WebPage.new_from_url(url, verify=False, timeout=8)
                url_used = url
                break
            except Exception:
                continue

        if not webpage:
            print(f"{Fore.RED}[!] Gagal mengakses {target}{Style.RESET_ALL}")
            return None

        # load wappalyzer
        wappalyzer = Wappalyzer.latest()
        technologies = sorted(list(wappalyzer.analyze(webpage)))

        # ambil juga headers HTTP
        headers_info = {}
        try:
            resp = session.get(url_used, timeout=8)
            headers_info = dict(resp.headers)
        except requests.RequestException as err:
            print(f"{Fore.RED}[!] Gagal ambil headers: {err}{Style.RESET_ALL}")

        result = {
            "target": url_used,
            "technologies": technologies,
            "headers": headers_info,
        }

        # tampilkan hasil di console
        if technologies:
            rows = [(i + 1, tech) for i, tech in enumerate(technologies)]
            print(tabulate(rows, headers=["No", "Technology"]))
        else:
            print(f"{Fore.RED}[!] Tidak ada teknologi terdeteksi{Style.RESET_ALL}")

        # simpan ke file (format JSON Lines)
        os.makedirs("results", exist_ok=True)
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

        print(f"{Fore.GREEN}[+] Hasil tersimpan di {output_file}{Style.RESET_ALL}")
        return result

    except Exception as err:
        print(f"{Fore.RED}[!] Error di tech_detect_enum: {err}{Style.RESET_ALL}")
        return None
