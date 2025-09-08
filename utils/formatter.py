from tabulate import tabulate
from colorama import Fore, Style
import json
import csv
import os

def print_result(result):
    """
    Format hasil scan biar lebih rapi dan keren
    """
    if not result:
        print(f"{Fore.RED}[!] Empty result{Style.RESET_ALL}")
        return

    if "error" in result:
        print(f"{Fore.RED}[!] Error: {result['error']}{Style.RESET_ALL}")
        return

    module = result.get("Module", "Unknown")
    target = result.get("Target", "-")

    print(f"\n{Fore.CYAN}=== {module} Result ==={Style.RESET_ALL}")
    print(f"Target: {Fore.YELLOW}{target}{Style.RESET_ALL}\n")

    # === khusus CMS
    if module.lower().startswith("cms"):
        cms = result.get("cms", "Not Detected")
        print(tabulate([[target, cms]], headers=["Target", "Detected CMS"], tablefmt="fancy_grid"))

    # === khusus DirBuster
    elif module.lower().startswith("dirbuster"):
        found = result.get("Found", [])
        if not found:
            print(f"{Fore.RED}No directories found.{Style.RESET_ALL}")
        else:
            rows = [(item.get("path"), item.get("status"), item.get("url")) for item in found]
            print(tabulate(rows, headers=["Path", "Status", "URL"], tablefmt="fancy_grid"))

    # === khusus Tech Detect
    elif module.lower().startswith("tech_detect"):
        techs = result.get("technologies", [])
        if not techs:
            techs = ["Not Detected"]

        print(tabulate(
            [[i + 1, t] for i, t in enumerate(techs)],
            headers=["No", "Technology"],
            tablefmt="fancy_grid"
        ))

    # === khusus Banner Grab
    elif "banners" in result:
        banners = result.get("banners", [])
        rows = [(b.get("port"), b.get("banner")) for b in banners]
        print(tabulate(rows, headers=["Port", "Banner"], tablefmt="fancy_grid"))

    # === khusus Subdomain Enum
    elif "subdomains" in result:
        subs = result.get("subdomains", [])
        rows = [[s] for s in subs]
        print(tabulate(rows, headers=["Subdomain"], tablefmt="fancy_grid"))

    # === fallback default
    else:
        rows = []
        for k, v in result.items():
            if isinstance(v, list):
                if v and isinstance(v[0], dict):
                    print(tabulate([list(d.values()) for d in v], headers=v[0].keys(), tablefmt="fancy_grid"))
                else:
                    rows.append((k, "; ".join(map(str, v))))
            elif k not in ["Module", "Target"]:
                rows.append((k, v))

        if rows:
            print(tabulate(rows, headers=["Key", "Value"], tablefmt="fancy_grid"))
        else:
            print(f"{Fore.YELLOW}[!] No data to display.{Style.RESET_ALL}")

    print(f"{Fore.GREEN}\n[✓] Done.{Style.RESET_ALL}\n")


def save_output(module_name, target, result, folder="results", ext="txt"):
    """
    Simpan hasil scan ke file:
    module_name + target + ekstensi
    - ext bisa 'json', 'txt', atau 'csv'
    """
    os.makedirs(folder, exist_ok=True)
    filename = os.path.join(folder, f"{module_name}_{target}.{ext}")

    if ext == "json":
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4, ensure_ascii=False)

    elif ext == "txt":
        with open(filename, "w", encoding="utf-8") as f:
            f.write(f"=== {result.get('Module', 'Unknown')} Result ===\n")
            f.write(f"Target: {result.get('Target', '-')}\n\n")
            for k, v in result.items():
                if isinstance(v, list):
                    f.write(f"{k}:\n")
                    for item in v:
                        if isinstance(item, dict):
                            f.write("  - " + json.dumps(item) + "\n")
                        else:
                            f.write(f"  - {item}\n")
                else:
                    f.write(f"{k}: {v}\n")

    elif ext == "csv":
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["Key", "Value"])
            for k, v in result.items():
                if isinstance(v, list):
                    if v and isinstance(v[0], dict):
                        writer.writerow([k, json.dumps(v)])
                    else:
                        writer.writerow([k, "; ".join(map(str, v))])
                else:
                    writer.writerow([k, v])

    else:
        raise ValueError("Unsupported file format. Gunakan 'json', 'txt', atau 'csv'")

    print(f"{Fore.GREEN}[+] Output saved to {filename}{Style.RESET_ALL}")
