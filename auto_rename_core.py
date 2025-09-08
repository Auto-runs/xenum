import os

folder = "core"

def main():
    for filename in os.listdir(folder):
        # Lewatkan __pycache__ dan folder lain
        if not filename.endswith(".py") or filename.startswith("__"):
            continue

        # Kalau file sudah ada "_enum.py", skip
        if filename.endswith("_enum.py"):
            continue

        # Ambil nama tanpa ekstensi
        base = filename[:-3]  # hapus ".py"

        # Rename jadi konsisten pakai "_enum.py"
        new_name = f"{base}_enum.py"
        old_path = os.path.join(folder, filename)
        new_path = os.path.join(folder, new_name)

        if os.path.exists(new_path):
            print(f"[-] {new_name} sudah ada, skip...")
        else:
            print(f"[+] Rename {filename} -> {new_name}")
            os.rename(old_path, new_path)

if __name__ == "__main__":
    main()
