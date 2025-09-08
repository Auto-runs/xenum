import importlib
import os
import sys
import time
import threading
from utils.formatter import print_result, save_output
from colorama import Fore, Style, init
from tabulate import tabulate
import pprint
import json

init(autoreset=True)

# ================= LOADING EFFECT ================= #
def loading_animation(text="Scanning in progress...", duration=5):
    spinner = ["|", "/", "-", "\\"]
    end_time = time.time() + duration
    i = 0
    while time.time() < end_time:
        sys.stdout.write(
            Fore.CYAN + f"\r{text} " + spinner[i % len(spinner)] + Style.RESET_ALL
        )
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    sys.stdout.write("\r" + " " * (len(text) + 4) + "\r")  # clear line

def fake_progress(text="Processing...", duration=5):
    steps = 30
    for i in range(steps + 1):
        percent = int((i / steps) * 100)
        bar = "█" * (i // 2) + "-" * ((steps // 2) - (i // 2))
        sys.stdout.write(
            Fore.YELLOW
            + f"\r{text} [{bar}] {percent}%"
            + Style.RESET_ALL
        )
        sys.stdout.flush()
        time.sleep(duration / steps)
    print("\n")

# ================================================== #

def center_text(text: str) -> str:
    try:
        width = os.get_terminal_size().columns
    except OSError:
        width = 80
    lines = text.rstrip("\n").splitlines()
    return "\n".join(line.center(width) for line in lines)

def banner():
    logo = r"""
__  _______ _   _ _   _ __  __ 
\ \/ / ____| \ | | | | |  \/  |
 \  /|  _| |  \| | | | | |\/| |
 /  \| |___| |\  | |_| | |  | |
/_/\_\_____|_| \_|\___/|_|  |_|

"""
    print(Fore.CYAN + center_text(logo) + Style.RESET_ALL)
    print(Fore.YELLOW + center_text("XEnumeration Toolkit v0.1"))
    print(Fore.MAGENTA + center_text("Author: Auto-runs") + Style.RESET_ALL + "\n")

def load_modules():
    modules = {}
    core_path = "core"
    files = [f[:-3] for f in os.listdir(core_path) if f.endswith(".py") and f != "__init__.py"]
    for i, mod in enumerate(sorted(files), start=1):
        modules[i] = mod
    return modules

def format_name(name: str) -> str:
    return " ".join(word.capitalize() for word in name.split("_"))

def sanitize_filename(name: str) -> str:
    return "".join(c for c in name if c.isalnum() or c in ("-", "_")).rstrip()

def save_output(module_name, target, result):
    folder = "results"
    os.makedirs(folder, exist_ok=True)
    filename = f"{folder}/{sanitize_filename(module_name)}_{sanitize_filename(target)}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        # Simpan sebagai JSON jika dict, biar lebih rapih
        if isinstance(result, (dict, list)):
            f.write(json.dumps(result, indent=4))
        else:
            f.write(str(result))
    print(Fore.YELLOW + f"[+] the result is saved to {filename}")

# ================= FORMATTER ================= #
def print_result(result):
    print(Fore.MAGENTA + "\n=== RESULTS ===")

    try:
        if isinstance(result, dict):
            if "banners" in result and isinstance(result["banners"], list):
                table = [(b.get("port", "-"), b.get("banner", "-")) for b in result["banners"]]
                print(tabulate(table, headers=["Port", "Banner"], tablefmt="fancy_grid"))

            elif "Found" in result and isinstance(result["Found"], list):
                if result["Found"] and isinstance(result["Found"][0], dict):
                    headers = list(result["Found"][0].keys())
                    rows = [[item.get(h, "") for h in headers] for item in result["Found"]]
                    print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
                else:
                    pprint.pprint(result)

            else:
                # fallback ke JSON biar rapi
                print(json.dumps(result, indent=4))

        elif isinstance(result, list):
            if all(isinstance(item, dict) for item in result):
                headers = list(result[0].keys())
                rows = [[item.get(h, "") for h in headers] for item in result]
                print(tabulate(rows, headers=headers, tablefmt="fancy_grid"))
            else:
                pprint.pprint(result)

        else:
            pprint.pprint(result)

    except Exception as e:
        print(Fore.RED + f"[!] Error formatting result: {e}")
        pprint.pprint(result)

    print(Fore.MAGENTA + "==================\n")

# ================================================== #

def main():
    banner()

    target = input(Fore.GREEN + "[?] Enter target (domain/IP): ").strip()
    MODULES = load_modules()

    while True:
        print(Fore.CYAN + "Choose the module you want to run:\n")
        for num, name in MODULES.items():
            print(f"  {num}. {format_name(name)}")
        print("  0. Keluar\n")

        try:
            choice = int(input(Fore.GREEN + ">> Select the module number: "))
        except ValueError:
            print(Fore.RED + "[!] Invalid choice!\n")
            continue

        if choice == 0:
            print(Fore.CYAN + "[*] bye... bye!")
            break

        module_name = MODULES.get(choice)
        if not module_name:
            print(Fore.RED + "[!] Module not found!\n")
            continue

        try:
            module = importlib.import_module(f"core.{module_name}")

            # 🔥 Efek Loading
            loading_animation("⚡ Running module...", duration=3)
            fake_progress("🚀 Loading The Scan", duration=4)

            if module_name == "asn_enum":
                asn_number = input(Fore.GREEN + "[?] Enter the ASN number (for example, 13335 for Cloudflare): ").strip()
                result = module.run(target, asn=asn_number)
            else:
                result = module.run(target)

            print_result(result)
            save_output(module_name, target, result)

        except Exception as e:
            print(Fore.RED + f"[!] Error while running the module {module_name}: {e}\n")

if __name__ == "__main__":
    main()
