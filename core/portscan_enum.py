# core/portscan.py
import socket
import threading
from queue import Queue
from colorama import Fore, Style, init

init(autoreset=True)  # Supaya warna auto-reset

try:
    import nmap  # pip install python-nmap
    HAS_NMAP = True
except ImportError:
    HAS_NMAP = False

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 3389, 8080]

def scan_port(target, port, timeout, results):
    """Scan single port (socket)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        if sock.connect_ex((target, port)) == 0:
            try:
                service = socket.getservbyport(port)
            except:
                service = "unknown"
            results.append({"port": port, "status": "open", "service": service})
        sock.close()
    except Exception:
        pass

def socket_scan(target, ports=None, top_ports=False, threads=100, timeout=1.0):
    """Port scan pake socket"""
    results = []
    q = Queue()

    # Tentukan list port
    if ports:
        port_list = [int(p.strip()) for p in ports.split(",")]
    elif top_ports:
        port_list = COMMON_PORTS
    else:
        port_list = range(1, 1025)  # default: 1-1024

    def worker():
        while not q.empty():
            port = q.get()
            scan_port(target, port, timeout, results)
            q.task_done()

    for port in port_list:
        q.put(port)

    threads_list = []
    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.start()
        threads_list.append(t)

    for t in threads_list:
        t.join()

    return results

def nmap_scan(target, ports=None, top_ports=False, args="-sV -T4"):
    """Port scan pake nmap"""
    if not HAS_NMAP:
        return None

    nm = nmap.PortScanner()
    if ports:
        port_range = ports
    elif top_ports:
        port_range = ",".join(str(p) for p in COMMON_PORTS)
    else:
        port_range = "1-1024"

    nm.scan(hosts=target, arguments=f"{args} -p {port_range}")
    results = []
    for proto in nm[target].all_protocols():
        for port in nm[target][proto].keys():
            state = nm[target][proto][port]["state"]
            service = nm[target][proto][port].get("name", "unknown")
            product = nm[target][proto][port].get("product", "")
            version = nm[target][proto][port].get("version", "")
            results.append({
                "port": port,
                "status": state,
                "service": service,
                "product": product,
                "version": version
            })
    return results

def pretty_output(results_dict):
    """Cetak hasil scan dengan format rapi"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}Module : {Fore.WHITE}{results_dict['Module']}")
    print(f"{Fore.YELLOW}Target : {Fore.WHITE}{results_dict['Target']}")
    print(f"{Fore.YELLOW}Mode   : {Fore.WHITE}{results_dict['Mode']}")
    if results_dict['Note']:
        print(f"{Fore.RED}Note   : {Fore.WHITE}{results_dict['Note']}")
    print(f"{Fore.CYAN}{'-'*60}")
    
    if results_dict['Open_Ports']:
        print(f"{Fore.GREEN}{'PORT':<8}{'STATUS':<10}{'SERVICE':<15}{'PRODUCT':<15}{'VERSION':<15}")
        print(f"{Fore.CYAN}{'-'*60}")
        for r in results_dict['Open_Ports']:
            port = str(r.get("port", ""))
            status = r.get("status", "")
            service = r.get("service", "")
            product = r.get("product", "")
            version = r.get("version", "")
            
            # Warna status
            if status.lower() == "open":
                status_color = Fore.GREEN
            elif status.lower() == "closed":
                status_color = Fore.RED
            else:
                status_color = Fore.YELLOW

            print(f"{Fore.WHITE}{port:<8}{status_color}{status:<10}{Fore.WHITE}{service:<15}{product:<15}{version:<15}")
    else:
        print(f"{Fore.RED}No open ports found.")
    
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}Total Open Ports: {Fore.WHITE}{results_dict['Total_Open']}\n")

def run(target, mode="socket", ports=None, top_ports=False, pretty=True):
    """
    mode = "socket" atau "nmap"
    pretty = True -> cetak hasil rapi
    """
    note = None

    if mode == "nmap":
        results = nmap_scan(target, ports=ports, top_ports=top_ports)
        if results is None:  # fallback kalau nmap ga ada
            note = "nmap not installed, fallback to socket"
            mode = "nmap (fallback → socket)"
            results = socket_scan(target, ports=ports, top_ports=top_ports)
    else:
        results = socket_scan(target, ports=ports, top_ports=top_ports)

    results_dict = {
        "Module": "Port Scan",
        "Target": target,
        "Mode": mode,
        "Total_Open": len(results),
        "Open_Ports": results,
        "Note": note
    }

    # Cetak hasil hanya sekali
    if pretty:
        pretty_output(results_dict)

    return results_dict

