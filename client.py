import socket
import random
import sys
import time
import uuid
from scapy.layers.dhcp import BOOTP, DHCP
from scapy.layers.inet import UDP, IP
from scapy.layers.l2 import Ether
from scapy.sendrecv import sendp, sniff
import http.server
import http.client
import requests

client_mac = uuid.getnode()
client_mac = (':'.join(['{:02x}'.format(
    (uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1]))
iface = "enp0s3"
dns_serverip = "127.0.0.1"
REDIRECT_SERVER_IP = "127.0.0.1"
REDIRECT_SERVER_PORT = 2746
clientip = "127.0.0.1"
clientport = 2060



# exponential growth for packet sending
def exponential_growth(previous_max: int, exponential_growth_rate: int):
    current_min = previous_max
    while True:
        yield (current_min, current_min * exponential_growth_rate)
        current_min *= exponential_growth_rate




def get_iface():
    netface = input(
        "Enter the network interface to use (e.g. enp0s3 / eth0): ")
    return netface


def send_dns(domain):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(domain.encode('utf-8'), (dns_serverip, 53))
    print("DNS request sent")
    ip_address, trash = sock.recvfrom(1024)
    ip_address = ip_address.decode('utf-8')
    print(f"Domain: {domain}, IP : {ip_address}")
    sock.close()


def dhcp_handler(netface):
    eth = Ether(src=client_mac, dst="ff:ff:ff:ff:ff:ff")
    ip = IP(src="0.0.0.0", dst="255.255.255.255")
    udp = UDP(sport=68, dport=67)
    bp = BOOTP(chaddr=client_mac, xid=random.randint(1, (2 ** 32) - 1))
    dhcp = DHCP(options=[("message-type", "discover"), 'end'])
    discover = eth / ip / udp / bp / dhcp
    sendp(discover, iface=netface)
    print("Discover packet sent, waiting for offer.")
    # wait for offer pkt
    pkt = sniff(iface=netface,
                filter=f"udp and (port 67 or port 68)", count=1)[0]
    print("OFFER PACKET RECEIVED")
    # build and send request packet
    if pkt and pkt.haslayer(DHCP):
        newIP = pkt[BOOTP].yiaddr
        eth = Ether(src=client_mac, dst="ff:ff:ff:ff:ff:ff")
        ip = IP(src="0.0.0.0", dst="255.255.255.255")
        udp = UDP(sport=68, dport=67)
        bp = BOOTP(chaddr=client_mac, yiaddr=newIP, xid=pkt[BOOTP].xid)
        dhcp = DHCP(options=[("message-type", "request"),
                    ("requested_addr", newIP), "end"])
        requestpkt = eth / ip / udp / bp / dhcp
        time.sleep(4)
        sendp(requestpkt, iface=netface)
        print("Request packet sent, waiting for Ack packet")
        # Get ack packet and print the IP given by DHCP
        ack = sniff(iface=netface,
                    filter=f"udp and (port 67 or port 68)", count=1)[0]
        if ack and ack.haslayer(DHCP):
            print("ACK PACKET RECEIVED")
            newIP = pkt[BOOTP].yiaddr
            print(f"assigned IP:{newIP}")
            return newIP


def client(server_address: tuple[str, int], filename: str, protocol: str, url: str) -> None:
    # server_prefix = f"{{{server_address[0]}:{server_address[1]}}}"

    # use tcp
    if (protocol == 'TCP' or protocol == 'tcp'):

            file_separated = filename.split('.')
            try:
                new_host = url.split('/')[2].split(':')[0]
                new_port = int(url.split('/')[2].split(':')[1])
                print("new host: ", new_host)
                print("new port: ", new_port)
                print()
                server_address = (new_host, new_port)

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as new_client_socket:
                    new_client_socket.connect(server_address)

                    # server_address = (new_host, int(new_port))

                    # client_socket.connect((new_host, new_port))
                    print("socket reconntected to new server")
                    # send GET_FILE request
                    request = f"GET_FILE {url} HTTP/1.1 \r\nHost: {server_address[0]} \r\nConnection: open \r\n\r\n"
                    print("GET_FILE request: ", request)

                    new_client_socket.send(request.encode('utf-8'))

                    # receive file_size in bytes
                    file_size = new_client_socket.recv(
                        8192).decode('utf-8')
                    print("file size is: ", file_size)
                    print()
                    file_size_tracker = 0
                    response = b''
                    while file_size_tracker <= int(file_size):
                        response = response + new_client_socket.recv(8192)
                        print("sizeof response: ", int(
                            sys.getsizeof(response)))
                        file_size_tracker = int(sys.getsizeof(response))

                    saved_filename = filename.split('.')[0] + '_saved'
                    saved_filename_extenstion = filename.split('.')[1]
                    with open(f'{saved_filename}.{saved_filename_extenstion}', 'wb') as file:
                        file.write(response)
                        print("file written correctly")

                    print("file received(finally!)")
                    return
            except Exception as e:
                print(f"{server_address} Unexpected error: {str(e)}")
    print(f"{server_address} Connection closed")

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    # use rudp
    if (protocol == 'RUDP' or protocol == 'rudp'):

        file_separated = filename.split('.')
        try:
            new_host = url.split('/')[2].split(':')[0]
            new_port = int(url.split('/')[2].split(':')[1])
            print("new host: ", new_host)
            print("new port: ", new_port)
            print()
            server_address = (new_host, new_port)
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as new_client_socket:
                new_client_socket.connect(server_address)

                print("socket reconntected to new server")
                # send RUDP_GET_FILE request
                request = f"RUDP_GET_FILE {url} HTTP/1.1 \r\nHost: {server_address[0]} \r\nConnection: open \r\n\r\n"
                print("RUDP_GET_FILE request: ", request)
                new_client_socket.send(request.encode('utf-8'))

                # receive file_size in bytes
                file_size = new_client_socket.recv(1024).decode('utf-8')
                print("file size is: ", file_size)
                print()
                # file_size_tracker = 0
                
                # receive amount of packets that we'll receive
                new_client_socket.send("SEND_ELEMS".encode('utf-8'))
                total_elems_response = new_client_socket.recv(1024).decode('utf-8')
                print("Total amount of elements in file_bytes_array: ", total_elems_response)

                # send ok to receive bytes of file
                new_client_socket.send("SEND_FILE_BYTES_ARRAY".encode('utf-8'))
                
                # Define Empty array for bytestream
                file_bytes_array = [None]* int(total_elems_response)

                # for loop to receive bytes
                
                for i in range(int(total_elems_response)):
                    
                    # recieve bytes of data up to 2^i * 1024
                    try:
                        new_client_socket.settimeout(3)
                        bytes_response = new_client_socket.recv(1024*(pow(2,i)))
                    except TimeoutError:
                        print("socket timed out, from no response or file complete transfer")
                        break
                
                    if bytes_response == None:
                        break
                    # bytes_response = new_client_socket.recv(1024*(pow(2,i)))
                    
                    # bytes_from_response = bytes_response.split(' ')
                    print()
                    file_bytes_array[i] = bytes_response
                    print("appended bytes")
                    if (i)==int(total_elems_response) - 1:
                        print("received all file exiting")
                counter = 0

                byte_stream = b''
                while(counter<int(total_elems_response)):
                    byte_stream += file_bytes_array[counter]
                    counter+=1

                saved_filename = filename.split('.')[0] + '_saved'
                saved_filename_extenstion = filename.split('.')[1]
                with open(f'{saved_filename}.{saved_filename_extenstion}', 'wb') as file:
                    file.write(byte_stream)
                        
                    

                # while file_size_tracker <= int(file_size):
                #     response = response + new_client_socket.recv(8192)
                #     print("sizeof response: ", int(
                #         sys.getsizeof(response)))
                #     file_size_tracker = int(sys.getsizeof(response))




                
                print("file received(finally!)")
                return

        except Exception as e:
            print(f"{server_address} Unexpected error: {str(e)}")
    print(f"{server_address} Connection closed")


def http_redirect(server_address: tuple[str, int], filename: str, protocol: str):
    headers = {'X-Auth-Token': protocol}
    url = f'http://{REDIRECT_SERVER_IP}:{REDIRECT_SERVER_PORT}/{filename}'
    response = requests.get(url, headers=headers, allow_redirects=False)
    # Check the status code and location header to see where we were redirected
    if response.status_code == 302:
        print(f'Redirected to: {response.headers["Location"]}')
        url = response.headers["Location"]
        client(server_address, filename, protocol, url)
    else:
        print(f'Error: {response.status_code}')


if __name__ == '__main__':
    while True:
        c = input(
            "Enter number: 1 - DNS , 2 - DHCP , 3 - TCP-HTTP-APP , 4 - RUDP-HTTP-APP , any other input will QUIT\n")
        if c == "1":
            domain = input("Please Enter the domain you want the Dns for:")
            if (domain == 'exit'):
                break
            else:
                send_dns(domain)
        elif c == "2":
            netface = get_iface()
            client_dhcp_ip = dhcp_handler(netface)
        elif c == "3":
            print("choose what to download")
            d = input(
                "Enter number: 1 - Image, 2 - Text file, Any other input will QUIT\n")
            if d == "1":
                server_address = (REDIRECT_SERVER_IP, REDIRECT_SERVER_PORT)
                filename = "image_tcp.jpg"
                protocol = 'TCP'
                http_redirect(server_address, filename, protocol)
                
            if d == "2":
                server_address = (REDIRECT_SERVER_IP, REDIRECT_SERVER_PORT)
                filename = "file_tcp.txt"
                protocol = 'TCP'
                http_redirect(server_address, filename, protocol)
                
        elif c == "4":
            print("choose what to download")
            d = input(
                "Enter number: 1 - Image, 2 - Text file, Any other input will QUIT\n")
            if d == "1":
                server_address = (REDIRECT_SERVER_IP, REDIRECT_SERVER_PORT)
                filename = "image_udp.jpg"
                protocol = 'RUDP'
                http_redirect(server_address, filename, protocol)
            if d == "2":
                server_address = (REDIRECT_SERVER_IP, REDIRECT_SERVER_PORT)
                filename = "file_udp.txt"
                protocol = 'RUDP'
                http_redirect(server_address, filename, protocol)
