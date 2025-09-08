import os
import re

def normalize_filename(name: str) -> str:
    # lowercase
    name = name.lower()

    # Benerin typo umum
    name = name.replace("detech", "detect")

    # Pisah dnsenum -> dns_enum
    name = re.sub(r"(dns)(enum)", r"\1_\2", name)

    # Hapus dobel _enum (contoh: rev_dns_enum_enum -> rev_dns_enum)
    name = re.sub(r"(_enum)+", "_enum", name)

    # Pastikan berakhiran _enum.py
    if not name.endswith("_enum.py"):
        name = re.sub(r"\.py$", "", name)  # hapus .py
        name = name + "_enum.py"

    return name


def fix_core_filenames(core_dir="core"):
    for filename in os.listdir(core_dir):
        if not filename.endswith(".py"):
            continue

        old_path = os.path.join(core_dir, filename)
        new_name = normalize_filename(filename)
        new_path = os.path.join(core_dir, new_name)

        if old_path != new_path:
            os.rename(old_path, new_path)
            print(f"[+] Rename {filename} -> {new_name}")


if __name__ == "__main__":
    fix_core_filenames()
