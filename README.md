<p align="center">
  <img src="https://img.shields.io/badge/XENUM-Enumeration%20Toolkit-blue?style=for-the-badge&logo=python" alt="XENUM">
</p>

<p align="center">
  <b>XENUM</b> is a modular enumeration toolkit with an interactive CLI interface.<br>
  Powered by <a href="https://github.com/Textualize/rich">rich</a> + <a href="https://pypi.org/project/pyfiglet/">pyfiglet</a>.
</p>

<p align="center">
  <a href="https://github.com/Auto-runs/XENUM/stargazers">
    <img src="https://img.shields.io/github/stars/Auto-runs/XENUM?style=social" alt="Stars">
  </a>
  <a href="https://github.com/Auto-runs/XENUM/issues">
    <img src="https://img.shields.io/github/issues/Auto-runs/XENUM" alt="Issues">
  </a>
  <a href="https://github.com/Auto-runs/XENUM/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/Auto-runs/XENUM" alt="License">
  </a>
  <img src="https://img.shields.io/badge/python-3.8%2B-blue" alt="Python">
</p>

---

## ✨ Features
- 📜 **Interactive menu** → choose modules directly from `main.py`
- 📊 **Output management**:
  - Results auto-saved in `results/` folder
  - JSON + TXT export
  - Pretty tables with [`tabulate`](https://pypi.org/project/tabulate/)
- 🎨 **Fancy UI**:
  - ASCII banner via `pyfiglet`
  - Spinner & fake progress bar with `rich`
- 🧩 **Modular design**:
  - Easily extendable, just drop new `.py` file into `core/`

---

## 📦 Available Modules (core/)
| Module                | Description |
|------------------------|-------------|
| `asn_enum.py`          | ASN enumeration & network info |
| `banner_grab_enum.py`  | Banner grabbing for service detection |
| `cms_enum.py`          | CMS detection (WordPress, Joomla, etc.) |
| `cve_lookup_enum.py`   | CVE vulnerability lookup |
| `dir_enum.py`          | Simple directory brute-forcing |
| `dirbuster_enum.py`    | Advanced directory enumeration |
| `dns_enum.py`          | DNS records enumeration (A, MX, TXT, etc.) |
| `http_enum.py`         | HTTP header & service checks |
| `portscan_enum.py`     | Basic port scanning |
| `rev_dns_enum.py`      | Reverse DNS lookup |
| `shodan_enum.py`       | Shodan API integration (requires API key) |
| `ssl_enum.py`          | SSL/TLS certificate enumeration |
| `subdomain_enum.py`    | Subdomain discovery |
| `tech_detect_enum.py`  | Web technology detection |
| `vuln_enum.py`         | Sensitive files detection (.env, phpinfo.php, etc.) |
| `wayback_enum.py`      | Wayback Machine historical URL fetch |
| `whois_enum.py`        | WHOIS lookup |

---

<p align="center"> <img src="demo.png" alt="demo" width="700"> </p>

---

## ⚙️ Installation
```bash
git clone https://github.com/Auto-runs/xenum.git
```
```bash
cd xenum
```
```bash
python -m venv venv
```
```bash
# Setup virtual environment
source venv/bin/activate   # Linux / Mac
```
```bash
venv\Scripts\activate      # Windows
```
```bash
# Install dependencies
pip install -r requirements.txt
```
```bash
python main.py
```
## flow example
__  _______ _   _ _   _ __  __ 
\ \/ / ____| \ | | | | |  \/  |
 \  /|  _| |  \| | | | | |\/| |
 /  \| |___| |\  | |_| | |  | |
/_/\_\_____|_| \_|\___/|_|  |_|

XEnumeration Toolkit v0.1
Author: Auto-runs

[?] Enter target (domain/IP): example.com

Choose the module you want to run:
  1. Asn Enum
  2. Wayback Enum
  0. Keluar

## preview 
[*] Mengambil data Wayback untuk example.com
[*] Mengecek apakah URL masih hidup di http://example.com
[1/20] http://web.archive.org/.../login.php -> Alive
[2/20] http://web.archive.org/.../admin/ -> Dead
...

## 📦 Output

Hasil tersimpan otomatis ke folder results/ dalam format:

JSON → structured result

TXT → simple list dengan status Alive/Dead

```bash
{
  "Module": "Wayback Machine Enumeration",
  "Target": "example.com",
  "Total": 5,
  "Wayback_URLs": [
    {
      "url": "http://example.com/admin.php",
      "status": "200",
      "alive": true,
      "real_url": "http://example.com/admin.php",
      "keywords": ["admin"]
    }
  ]
}
```
