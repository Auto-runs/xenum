# core/banner_grab.py
import socket
import json
import os
from colorama import Fore, Style
import concurrent.futures

COMMON_PORTS = [21, 22, 25, 80, 110, 143, 443, 587, 3306, 8080]


def grab_banner(target, port):
    """
    Coba ambil banner dari port
    """
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect((target, port))

        # kalau HTTP/HTTPS, coba kirim request biar ada respon
        if port in [80, 8080, 443]:
            s.send(b"HEAD / HTTP/1.0\r\nHost: %b\r\n\r\n" % target.encode())

        banner = s.recv(1024).decode(errors="ignore").strip()
        s.close()

        # selalu string, jangan list
        return {"port": port, "banner": banner if banner else "N/A"}

    except Exception:
        return {"port": port, "banner": "Timeout/Closed"}


def run(target, ports=COMMON_PORTS, threads=10, output_file="results/banner_grab.json"):
    """
    Banner Grabbing multi-threaded
    """
    results = {"Module": "Banner Grabbing", "Target": target, "banners": []}

    print(f"{Fore.YELLOW}[*] Banner grabbing {target} pada {len(ports)} port...{Style.RESET_ALL}")

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {executor.submit(grab_banner, target, port): port for port in ports}
        for future in concurrent.futures.as_completed(futures):
            res = future.result()
            results["banners"].append(res)
            if res["banner"] != "Timeout/Closed":
                print(f"{Fore.GREEN}[+] {target}:{res['port']} -> {res['banner']}{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}[-] {target}:{res['port']} closed{Style.RESET_ALL}")

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
