# core/rev_dnsenum.py
import socket
import ipaddress
import concurrent.futures
import os
import json
from colorama import Fore, Style

def reverse_dns(ip):
    """
    Resolve hostname dari 1 IP
    """
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except (socket.herror, socket.gaierror, TimeoutError):
        return None

def run(target, limit=50, threads=20, output_file="results/rev_dns_enum.json"):
    """
    Reverse DNS Enumeration
    :param target: CIDR (contoh: 192.168.1.0/24)
    :param limit: maksimal IP yang di-resolve
    :param threads: jumlah worker untuk parallel lookup
    """
    results = {
        "Module": "Reverse DNS Enumeration",
        "Target": target,
        "Resolved": [],
        "Total_Resolved": 0
    }

    try:
        network = ipaddress.ip_network(target, strict=False)
        ips = [str(ip) for ip in network.hosts()][:limit]

        print(f"{Fore.YELLOW}[*] Reverse DNS scan {target} (max {limit} IPs, {threads} threads){Style.RESET_ALL}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
            future_to_ip = {executor.submit(reverse_dns, ip): ip for ip in ips}
            for future in concurrent.futures.as_completed(future_to_ip):
                ip = future_to_ip[future]
                hostname = future.result()
                if hostname:
                    results["Resolved"].append({
                        "ip": ip,
                        "hostname": hostname
                    })
                    print(f"{Fore.GREEN}[+] {ip} -> {hostname}{Style.RESET_ALL}")

        results["Total_Resolved"] = len(results["Resolved"])

    except ValueError as e:
        results["Error"] = str(e)
        print(f"{Fore.RED}[!] Error: {e}{Style.RESET_ALL}")

    # Simpan hasil
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

    print(f"{Fore.CYAN}[+] Hasil tersimpan di {output_file}{Style.RESET_ALL}")
    return results
