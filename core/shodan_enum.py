# core/shodan_enum.py
import requests

def run(query, api_key=None, limit=20):
    """
    Shodan search untuk menemukan service exposed.
    
    Parameters:
    -----------
    query   : str  -> keyword Shodan (contoh: "apache", "nginx", "port:22")
    api_key : str  -> API key Shodan (jika None, user diminta input manual)
    limit   : int  -> maksimal hasil yang ditampilkan
    """

    # Jika api_key tidak diberikan, minta user isi manual
    if not api_key:
        api_key = input("[?] Enter your Shodan API Key: ").strip()
        if not api_key:
            return {"Error": "Shodan API key must not be empty!"}

    results = {
        "Module": "Shodan Enumeration",
        "Query": query,
        "Matches": [],
        "Total_Matches": 0
    }

    url = f"https://api.shodan.io/shodan/host/search?key={api_key}&query={query}&limit={limit}"

    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        if "matches" in data:
            for match in data["matches"][:limit]:
                results["Matches"].append({
                    "ip": match.get("ip_str"),
                    "port": match.get("port"),
                    "org": match.get("org"),
                    "hostnames": match.get("hostnames"),
                    "location": match.get("location"),
                    "timestamp": match.get("timestamp")
                })

            results["Total_Matches"] = len(results["Matches"])
        else:
            results["Error"] = data.get("error", "No results found.")

    except requests.HTTPError as http_err:
        if resp.status_code == 403:
            results["Error"] = (
                "403 Forbidden: Your API Key does not have access to the Shodan Search API.👉 /n "
                "Solution: Upgrade your Shodan account to Membership ($49 one-time payment) to use this feature.."
            )
        else:
            results["Error"] = f"HTTP error: {http_err}"
    except requests.RequestException as e:
        results["Error"] = f"Request error: {str(e)}"
    except ValueError:
        results["Error"] = "Gagal decode JSON dari Shodan API."

    return results
