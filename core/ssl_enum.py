# core/ssl_enum.py
import ssl
import socket
from datetime import datetime
import os
import json
from colorama import Fore, Style

def run(target, port=443, output_file="results/ssl_enum.json"):
    """
    Enumerasi SSL/TLS Certificate dari target:port
    - Ambil Subject, Issuer
    - Ambil SAN (Subject Alternative Name)
    - Hitung sisa validitas (days left)
    - Simpan hasil ke JSON
    """
    ctx = ssl.create_default_context()
    results = {
        "Module": "SSL/TLS Enumeration",
        "Target": target,
        "Port": port
    }

    try:
        with socket.create_connection((target, port), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=target) as ssock:
                cert = ssock.getpeercert()

                not_before = cert.get("notBefore")
                not_after = cert.get("notAfter")
                expired = None
                days_left = None

                if not_after:
                    try:
                        expire_date = datetime.strptime(
                            not_after, "%b %d %H:%M:%S %Y %Z"
                        )
                        expired = expire_date < datetime.utcnow()
                        days_left = (expire_date - datetime.utcnow()).days
                    except Exception:
                        expired = None

                san = []
                for ext in cert.get("subjectAltName", []):
                    san.append(ext[1])

                results.update({
                    "Subject": dict(x[0] for x in cert.get("subject", [])),
                    "Issuer": dict(x[0] for x in cert.get("issuer", [])),
                    "Valid_From": not_before,
                    "Valid_Until": not_after,
                    "Expired": expired,
                    "Days_Left": days_left,
                    "SAN": san
                })

    except Exception as e:
        results["Error"] = str(e)
        print(f"{Fore.RED}[!] SSL error: {e}{Style.RESET_ALL}")

    # Simpan hasil ke file
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

    print(f"{Fore.GREEN}[+] SSL data {target}:{port} tersimpan di {output_file}{Style.RESET_ALL}")
    return results
