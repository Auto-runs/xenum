# core/dns_enum.py
import dns.resolver
import json
import os
from colorama import Fore, Style

RECORD_TYPES = ["A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"]

def query_record(domain, rtype):
    try:
        answers = dns.resolver.resolve(domain, rtype, lifetime=5)
        return [r.to_text() for r in answers]
    except Exception as e:
        return [f"Error: {str(e)}"]

def run(domain, output_file="results/dns_enum.json"):
    """
    DNS Enumeration:
    - A, AAAA
    - MX, NS
    - TXT, CNAME, SOA
    """
    results = {"Module": "DNS Enumeration", "Target": domain, "Records": {}}

    for rtype in RECORD_TYPES:
        records = query_record(domain, rtype)
        results["Records"][rtype] = records

        if records and not records[0].startswith("Error"):
            print(f"{Fore.GREEN}[+] {rtype} → {records}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[-] {rtype} → {records}{Style.RESET_ALL}")

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

    old_data.append(results)
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(old_data, f, indent=2, ensure_ascii=False)

    print(f"{Fore.CYAN}[+] Hasil DNS Enum tersimpan di {output_file}{Style.RESET_ALL}")
    return results
