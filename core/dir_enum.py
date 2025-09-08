# core/dir_enum.py
import requests
import os

DEFAULT_WORDLIST = [
    "admin", "login", "uploads", "config", "backup", "dashboard", "api", "test"
]

def load_wordlist(wordlist_path):
    if not wordlist_path or not os.path.isfile(wordlist_path):
        return DEFAULT_WORDLIST
    
    with open(wordlist_path, "r", encoding="utf-8", errors="ignore") as f:
        return [line.strip() for line in f if line.strip()]

def dir_bruteforce(target, scheme="http", wordlist=None):
    """Bruteforce direktori umum"""
    dirs = wordlist
    base_url = f"{scheme}://{target}"
    results = []

    for d in dirs:
        url = f"{base_url}/{d}/"
        try:
            resp = requests.get(url, timeout=5, verify=False)
            if resp.status_code in [200, 301, 302, 403]:
                results.append({
                    "dir": d,
                    "url": url,
                    "status": resp.status_code
                })
        except requests.exceptions.RequestException:
            continue

    return results

def run(target, scheme="http", wordlist_path=None):
    """
    Main function Directory Enumeration
    Bisa pakai wordlist default atau custom (txt file)
    """
    results = {
        "Module": "Directory Enumeration",
        "Target": target,
        "Found_Directories": []
    }

    try:
        # load wordlist
        dirs = load_wordlist(wordlist_path)

        print(f"[+] Menjalankan Directory Bruteforce pada {target}")
        print(f"[+] Total wordlist: {len(dirs)}")

        results["Found_Directories"] = dir_bruteforce(target, scheme, dirs)
    except Exception as e:
        results["Error"] = str(e)

    return results
