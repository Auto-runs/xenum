# core/cve_lookup_enum.py
import json
import os
import requests
import time
import sys
import threading
from tabulate import tabulate
from colorama import Fore, Style

BANNER_MAP = {
    "apache tomcat": ("apache", "tomcat"),
    "apache": ("apache", "http_server"),
    "nginx": ("nginx", "nginx"),
    "microsoft-iis": ("microsoft", "iis"),
    "iis": ("microsoft", "iis"),
    "openresty": ("openresty", "openresty"),
    "lighttpd": ("lighttpd", "lighttpd"),
    "litespeed": ("litespeedtech", "litespeed"),
    "jetty": ("eclipse", "jetty"),
    "gws": ("google", "gws"),
    "caddy": ("caddyserver", "caddy"),
    "express": ("nodejs", "express"),
    "node.js": ("nodejs", "nodejs"),
}

def detect_from_banner(banner_text: str):
    banner_text = banner_text.lower()
    for key, (vendor, product) in BANNER_MAP.items():
        if key in banner_text:
            return vendor, product
    return None, None

def spinner(text="Scanning"):
    spinner_cycle = ['|', '/', '-', '\\']
    done_flag = {"stop": False}

    def run_spinner():
        i = 0
        while not done_flag["stop"]:
            sys.stdout.write(f"\r{text} {spinner_cycle[i % len(spinner_cycle)]}")
            sys.stdout.flush()
            i += 1
            time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(text) + 4) + "\r")

    t = threading.Thread(target=run_spinner)
    t.daemon = True
    t.start()
    return lambda: done_flag.update({"stop": True})

def format_results(results):
    # === Multiple vendors mode ===
    if isinstance(results["CVE_Results"], list) and results["Vendor"] is None:
        print(f"\n{Fore.CYAN}=== CVE Lookup Multi-Vendor Result ==={Style.RESET_ALL}")
        print(f"Target : {Fore.YELLOW}{results.get('Target', '-')}{Style.RESET_ALL}\n")
        for res in results["CVE_Results"]:
            vendor = res.get("Vendor", "-")
            product = res.get("Product", "-")
            cves = res.get("CVE_List", [])
            print(f"{Fore.MAGENTA}--- {vendor}/{product} ---{Style.RESET_ALL}")
            if not cves:
                print(f"{Fore.RED}[!] Tidak ada CVE ditemukan.{Style.RESET_ALL}\n")
                continue
            rows = []
            for cve in cves:
                rows.append([
                    cve.get("id", "-"),
                    cve.get("cvss", "-"),
                    (cve.get("summary", "-")[:80] + "...") if cve.get("summary") and len(cve.get("summary")) > 80 else cve.get("summary", "-")
                ])
            print(tabulate(rows, headers=["CVE ID", "CVSS", "Summary"], tablefmt="fancy_grid"))
            print()
        return

    # === Single vendor mode ===
    if "Error" in results:
        print(f"{Fore.RED}[!] Error: {results['Error']}{Style.RESET_ALL}")
        return

    vendor = results.get("Vendor", "-")
    product = results.get("Product", "-")
    cves = results.get("CVE_Results", [])

    print(f"\n{Fore.CYAN}=== CVE Lookup Result ==={Style.RESET_ALL}")
    print(f"Target : {Fore.YELLOW}{results.get('Target', '-')}{Style.RESET_ALL}")
    print(f"Vendor : {Fore.YELLOW}{vendor}{Style.RESET_ALL}")
    print(f"Product: {Fore.YELLOW}{product}{Style.RESET_ALL}\n")

    if not cves:
        print(f"{Fore.RED}[!] Tidak ada CVE ditemukan.{Style.RESET_ALL}")
        return

    rows = []
    for cve in cves:
        rows.append([
            cve.get("id", "-"),
            cve.get("cvss", "-"),
            (cve.get("summary", "-")[:80] + "...") if cve.get("summary") and len(cve.get("summary")) > 80 else cve.get("summary", "-")
        ])

    print(tabulate(rows, headers=["CVE ID", "CVSS", "Summary"], tablefmt="fancy_grid"))
    print(f"\n{Fore.GREEN}[✓] Done.{Style.RESET_ALL}\n")

def run(target):
    results = {
        "Module": "CVE Lookup",
        "Target": target,
        "Vendor": None,
        "Product": None,
        "CVE_Results": []
    }

    banner_file = "results/banner_grab.json"
    vendor, product = None, None

    # === 1. coba auto detect dari banner ===
    if os.path.exists(banner_file):
        try:
            with open(banner_file, "r", encoding="utf-8") as f:
                banner_data = json.load(f)
                banners = banner_data.get("banners", [])
                if isinstance(banners, list):
                    for b in banners:
                        banner_text = str(b.get("banner", ""))
                        v, p = detect_from_banner(banner_text)
                        if v and p:
                            vendor, product = v, p
                            break
        except Exception as e:
            results["Error"] = f"Gagal baca banner_grab.json: {e}"

    # === 2. Manual input ===
    if not vendor or not product:
        print("[!] Tidak bisa deteksi otomatis dari banner.")
        vendor = input("Masukkan vendor (contoh: apache): ").strip()
        product = input("Masukkan produk (contoh: http_server): ").strip()

        # === 3. Kalau input kosong -> scan semua vendor di BANNER_MAP ===
        if not vendor and not product:
            print(f"\n{Fore.YELLOW}[!] Input kosong, mencoba semua mapping...{Style.RESET_ALL}")
            all_cve_results = []

            for v, p in BANNER_MAP.values():
                print(f"\n{Fore.CYAN}Scanning {v}/{p}...{Style.RESET_ALL}")
                stop_spin = spinner("Scanning CVEs")
                try:
                    url = f"https://cve.circl.lu/api/search/{v}/{p}"
                    r = requests.get(url, timeout=10)
                    if r.status_code == 200:
                        cves = r.json()
                        if isinstance(cves, list) and cves:
                            all_cve_results.append({
                                "Vendor": v,
                                "Product": p,
                                "CVE_List": cves[:10]
                            })
                except Exception as e:
                    pass
                stop_spin()

            results["CVE_Results"] = all_cve_results
            format_results(results)
            return results

    # === 4. Fallback default ===
    if not vendor:
        vendor = "apache"
    if not product:
        product = "http_server"

    results["Vendor"] = vendor
    results["Product"] = product

    # === 5. Spinner + request ===
    print(f"\n{Fore.YELLOW}🚀 Executing CVE Lookup Scan...{Style.RESET_ALL}\n")
    stop_spin = spinner("Scanning CVEs")
    try:
        url = f"https://cve.circl.lu/api/search/{vendor}/{product}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            cves = r.json()
            if isinstance(cves, list) and cves:
                results["CVE_Results"] = cves[:10]
            else:
                results["Error"] = "Tidak ada CVE ditemukan."
        else:
            results["Error"] = f"HTTP Error {r.status_code}"
    except Exception as e:
        results["Error"] = f"Gagal fetch CVE API: {e}"
    stop_spin()

    format_results(results)
    return results
