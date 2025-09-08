# core/whois_enum.py
import whois
import os
import json
from colorama import Fore, Style

def clean_field(value):
    """Helper untuk normalisasi field yang bisa berupa list/datetime"""
    if isinstance(value, list):
        return [str(v) for v in value if v]
    if value:
        return str(value)
    return None

def run(domain, output_file="results/whois_enum.json"):
    """
    Whois Enumeration
    :param domain: domain target
    :param output_file: file JSON hasil simpan
    """
    results = {"Module": "Whois Enumeration", "Target": domain}
    try:
        w = whois.whois(domain)
        results.update({
            "domain_name": clean_field(w.domain_name),
            "registrar": clean_field(w.registrar),
            "creation_date": clean_field(w.creation_date),
            "expiration_date": clean_field(w.expiration_date),
            "updated_date": clean_field(w.updated_date),
            "name_servers": clean_field(w.name_servers),
            "emails": clean_field(w.emails)
        })

    except Exception as e:
        results["error"] = str(e)
        print(f"{Fore.RED}[!] WHOIS lookup error: {e}{Style.RESET_ALL}")

    # simpan hasil ke file
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

    print(f"{Fore.GREEN}[+] WHOIS data untuk {domain} tersimpan di {output_file}{Style.RESET_ALL}")
    return results
