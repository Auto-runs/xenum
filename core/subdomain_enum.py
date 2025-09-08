# core/subdomain_enum_pro.py
import aiohttp
import asyncio
import socket
import os
import json
import csv
from tqdm.asyncio import tqdm
from colorama import Fore, Style

# Path default wordlist
DEFAULT_WORDLIST_FILE = os.path.join("wordlists", "subenum.txt")

async def resolve_subdomain(session, sub, domain, timeout=3):
    """
    Resolve subdomain ke IP (async).
    """
    full = f"{sub.strip()}.{domain}"
    try:
        loop = asyncio.get_event_loop()
        ip = await loop.getaddrinfo(full, None, family=socket.AF_INET)
        return {"subdomain": full, "ip": ip[0][4][0]}
    except Exception:
        return None

async def brute_force_enum(domain, wordlist_file=None, concurrency=100):
    """ Async brute force subdomain enumeration """
    wordlist_path = wordlist_file or DEFAULT_WORDLIST_FILE
    if not os.path.isfile(wordlist_path):
        return [{"error": f"Wordlist tidak ditemukan: {wordlist_path}"}]

    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        subs = [line.strip() for line in f if line.strip()]

    print(f"[+] Starting brute force subdomain enum on: {domain}")
    print(f"[i] Loaded {len(subs)} words from {wordlist_path}\n")

    results = []
    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [resolve_subdomain(session, sub, domain) for sub in subs]

        for coro in tqdm.as_completed(tasks, desc=f"[Brute] {domain}", unit="sub"):
            res = await coro
            if res:
                results.append(res)
                print(f"{Fore.GREEN}[+] Found: {res['subdomain']} -> {res['ip']}{Style.RESET_ALL}")

    return results

async def osint_enum(domain):
    """ Enumerasi subdomain via OSINT (crt.sh) """
    url = f"https://crt.sh/?q=%25.{domain}&output=json"
    results = []
    print(f"[+] Starting OSINT subdomain enum on: {domain}")

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as r:
                if r.status == 200:
                    data = await r.json(content_type=None)
                    subdomains = set()
                    for entry in data:
                        name = entry.get("name_value")
                        if name:
                            for sub in name.split("\n"):
                                if sub.strip() and "*" not in sub:
                                    subdomains.add(sub.strip())

                    print(f"[i] Found {len(subdomains)} potential subdomains via crt.sh\n")

                    for sub in subdomains:
                        try:
                            ip = socket.gethostbyname(sub)
                            results.append({"subdomain": sub, "ip": ip})
                            print(f"{Fore.YELLOW}[OSINT] {sub} -> {ip}{Style.RESET_ALL}")
                        except:
                            results.append({"subdomain": sub, "ip": None})

    except Exception as e:
        results.append({"error": str(e)})

    return results

def save_results(results, target):
    os.makedirs("results", exist_ok=True)

    json_file = f"results/subdomain_enum_{target}.json"
    csv_file = f"results/subdomain_enum_{target}.csv"

    # simpan ke JSON
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # simpan ke CSV
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["subdomain", "ip"])
        writer.writeheader()
        writer.writerows(results)

    return json_file, csv_file

def run(target, wordlist_file=None, mode="both"):
    """
    Main entry point
    - target: domain utama
    - wordlist_file: optional file wordlist
    - mode: "brute", "osint", atau "both"
    """
    results = []

    if mode in ("brute", "both"):
        results.extend(asyncio.run(brute_force_enum(target, wordlist_file)))

    if mode in ("osint", "both"):
        results.extend(asyncio.run(osint_enum(target)))

    # hapus duplikat
    unique = {item.get("subdomain"): item for item in results if "subdomain" in item}
    results = list(unique.values())

    # simpan hasil
    json_file, csv_file = save_results(results, target)

    print(f"\n[✓] Subdomain enumeration finished for {target}")
    print(f"[+] Total found: {len(results)}")
    print(f"[+] Results saved to:\n - {json_file}\n - {csv_file}")

    return {
        "Module": "Subdomain Enumeration Pro",
        "Target": target,
        "Total_Found": len(results),
        "Resolved": results,
        "Output_JSON": json_file,
        "Output_CSV": csv_file
    }
