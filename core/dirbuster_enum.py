# core/dirbuster_enum.py
import aiohttp
import asyncio
import urllib3
import random
import os
import json
import csv
from tqdm import tqdm
from colorama import Fore, Style

# disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (X11; Linux x86_64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)",
    "Mozilla/5.0 (XenEnum-DirBuster)"
]

async def fetch(session, url, path, valid_codes, timeout, sem):
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    async with sem:  # batasi concurrency
        try:
            async with session.get(url, headers=headers, timeout=timeout, ssl=False) as resp:
                if resp.status in valid_codes:
                    size = int(resp.headers.get("Content-Length", 0)) or len(await resp.read())
                    return {
                        "path": path,
                        "status": resp.status,
                        "size": size,
                        "url": str(resp.url)
                    }
        except Exception:
            return None
    return None

async def run_async(target, wordlist, scheme, valid_codes, timeout, concurrency):
    base_url = f"{scheme}://{target}"
    os.makedirs("results", exist_ok=True)

    try:
        with open(wordlist, "r", encoding="utf-8", errors="ignore") as f:
            paths = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return {"error": f"Wordlist {wordlist} tidak ditemukan"}
    if not paths:
        return {"error": "Wordlist kosong"}

    results = []
    sem = asyncio.Semaphore(concurrency)
    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = [fetch(session, f"{base_url}/{path}", path, valid_codes, timeout, sem) for path in paths]

        # progress bar yang smooth
        for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc=f"[DirBuster] Scanning {target}", unit="path"):
            res = await coro
            if res:
                results.append(res)
                # tampilkan hasil langsung
                if res["status"] == 200:
                    color = Fore.GREEN
                elif res["status"] in [301, 302]:
                    color = Fore.YELLOW
                elif res["status"] == 403:
                    color = Fore.RED
                else:
                    color = Fore.WHITE
                print(f"{color}[{res['status']}] {res['url']} ({res['size']} bytes){Style.RESET_ALL}")

    # simpan ke JSON
    json_file = f"results/dirbuster_{target.replace('.', '')}.json"
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # simpan ke CSV
    csv_file = f"results/dirbuster_{target.replace('.', '')}.csv"
    with open(csv_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["path", "status", "size", "url"])
        writer.writeheader()
        writer.writerows(results)

    return {
        "Module": "DirBuster-Pro",
        "Target": target,
        "Total_Found": len(results),
        "Found": results,
        "Output_JSON": json_file,
        "Output_CSV": csv_file
    }

def run(target, wordlist="wordlists/common.txt", scheme="http",
        valid_codes=None, timeout=5, concurrency=20):
    
    if valid_codes is None:
        valid_codes = [200, 301, 302, 403]
    
    return asyncio.run(run_async(target, wordlist, scheme, valid_codes, timeout, concurrency))
