import socket
import time

dns_ip = "127.0.0.1"
dns_port = 53
# Dictionary to store IP address mappings
dns_cache = {"www.doryevhttp.com": "127.0.0.1"}


def check_internet():
    try:
        socket.getaddrinfo("www.google.com", None)
        return True
    except socket.gaierror:
        return False


def dns_reply():
    domain, client_ip = sock.recvfrom(1024)
    domain = domain.decode('utf-8')
    if domain in dns_cache:
        ip_address = dns_cache[domain]
        print(f"{domain} : {dns_cache[domain]}")
        if check_internet():
            sock.sendto(ip_address.encode('utf-8'), client_ip)
            print("IP SENT")
            print(f"Domain: {domain} , IP : {ip_address}")

    else:
        if check_internet():
            try:
                ip_address = socket.gethostbyname(domain)
                dns_cache[domain] = ip_address
                sock.sendto(ip_address.encode('utf-8'), client_ip)
                print("IP SENT")
                print(f"Domain: {domain} , IP : {ip_address}")

            except socket.gaierror:
                print("Could not resolve domain / no internet connection")
                ip_address = "Couldn't Resolve"
                sock.sendto(ip_address.encode('utf-8'), client_ip)


if __name__ == '__main__':
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((dns_ip, 53))
    print("DNS SERVER IS ON...")
    # Start sniffing DNS queries on port 53 on the specified interface
    while True:
        dns_reply()
        time.sleep(1)
