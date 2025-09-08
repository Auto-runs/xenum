# core/asn_enum.py
import requests
import socket
import json
import os
from ipwhois import IPWhois
from colorama import Fore, Style

ASN_API = "https://api.bgpview.io/asn"

def fetch_asn_info(asn):
    """
    Ambil info ASN dari BGPView API
    """
    url = f"{ASN_API}/{asn}/prefixes"
    results = {
        "ASN": asn,
        "ipv4_prefixes": [],
        "ipv6_prefixes": []
    }

    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("status") == "ok":
                for prefix in data["data"]["ipv4_prefixes"]:
                    results["ipv4_prefixes"].append({
                        "prefix": prefix.get("prefix"),
                        "name": prefix.get("name"),
                        "description": prefix.get("description")
                    })
                for prefix in data["data"]["ipv6_prefixes"]:
                    results["ipv6_prefixes"].append({
                        "prefix": prefix.get("prefix"),
                        "name": prefix.get("name"),
                        "description": prefix.get("description")
                    })
            else:
                results["error"] = "Invalid API response"
        else:
            results["error"] = f"API error: {r.status_code}"
    except Exception as e:
        results["error"] = str(e)

    return results


def resolve_asn_from_domain(domain):
    """
    Resolve domain -> IP -> ASN
    """
    try:
        ip = socket.gethostbyname(domain)
        obj = IPWhois(ip)
        res = obj.lookup_rdap()
        asn = res.get("asn")
        asn_desc = res.get("asn_description")
        return {"ip": ip, "asn": asn, "asn_description": asn_desc}
    except Exception as e:
        return {"error": str(e)}


def run(target, asn=None, output_file="results/asn_enum.json"):
    """
    ASN Enumeration:
    - Bisa input domain (otomatis resolve ke ASN)
    - Atau langsung input ASN
    - Simpan hasil ke JSON
    """
    results = {
        "Module": "ASN Enumeration",
        "Target": target,
        "ASN_Info": {}
    }

    # === Auto resolve jika user kasih domain tanpa ASN ===
    if not asn:
        print(f"{Fore.YELLOW}[*] Mencoba resolve ASN dari domain: {target}{Style.RESET_ALL}")
        res = resolve_asn_from_domain(target)
        if "error" in res:
            results["Error"] = res["error"]
            print(f"{Fore.RED}[!] Gagal resolve ASN: {res['error']}{Style.RESET_ALL}")
            return results
        asn = res["asn"]
        results["Resolved"] = res
        print(f"{Fore.GREEN}[+] ASN {asn} ({res['asn_description']}) ditemukan untuk {res['ip']}{Style.RESET_ALL}")

    print(f"{Fore.YELLOW}[*] Mengambil prefix dari ASN {asn}{Style.RESET_ALL}")
    info = fetch_asn_info(asn)
    results["ASN_Info"] = info

    if "error" not in info:
        print(f"{Fore.GREEN}[+] ASN {asn} IPv4 Prefixes: {len(info['ipv4_prefixes'])}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[+] ASN {asn} IPv6 Prefixes: {len(info['ipv6_prefixes'])}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}[!] Error: {info['error']}{Style.RESET_ALL}")

    # === Save ke JSON ===
    os.makedirs("results", exist_ok=True)
    if os.path.exists(output_file):
        try:
            with open(output_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
        except json.JSONDecodeError:
            old_data = []
    else:
        old_data = []

    old_data.append(results)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(old_data, f, indent=2, ensure_ascii=False)

    print(f"{Fore.CYAN}[+] Hasil ASN Enum tersimpan di {output_file}{Style.RESET_ALL}")
    return results
