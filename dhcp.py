import time
import uuid
from scapy.layers.dhcp import DHCP, BOOTP
from scapy.layers.inet import IP, UDP
from scapy.layers.l2 import Ether
from scapy.sendrecv import sendp, sniff

# Getting the Mac number of the server.
sender_mac = uuid.getnode()
sender_mac = (':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2 * 6, 2)][::-1]))
iface = "enp0s3"
dhcp_ip = "127.0.0.1"
dhcp_fake_ip = "127.0.0.3"
IP_POOL = ['127.0.0.%d' % i for i in range(5, 255)]
IP_MAPPINGS = {}  # Client MAC -> IP mappings
dhcp_port = 68
client_port = 67

#get_iface() - Asking the user to write the network interface he will use for the current session
def get_iface():
    netface = input("Enter the network interface to use (e.g. enp0s3 / eth0): ")
    return netface

#get_ip() - gives ip to the user, only if the ip is not taken
def get_ip():
    for ip in IP_POOL:
        if ip not in IP_MAPPINGS:
            IP_MAPPINGS[ip] = False
            return ip
    raise Exception("No available IP addresses")

# ack_pkt() - after we get the request packet from the client we create Ack packet and send it to the client,
# the ack packet will tell the client that the IP the offer pkt sent approved or not.
def ack_pkt(packet, netface):
    print("REQUEST PACKET RECEIVED")
    client_newip = packet[BOOTP].yiaddr
    if not IP_MAPPINGS[client_newip]:
        IP_MAPPINGS[client_newip] = True
        print(f"{client_newip} assigned")
    else:
        print("IP NOT AVAILABLE")

    mac = packet[BOOTP].chaddr
    transactionID = packet[BOOTP].xid
    ether = Ether(src=sender_mac, dst=mac)
    ip = IP(src=dhcp_fake_ip, dst="255.255.255.255")
    udp = UDP(sport=67, dport=68)
    bp = BOOTP(op=2, yiaddr=packet[BOOTP].yiaddr, siaddr=packet[BOOTP].siaddr, chaddr=packet[BOOTP].chaddr,
               xid=transactionID)
    dhcp = DHCP(options=[("message-type", "ack"),
                         'end'])
    ack = ether / ip / udp / bp / dhcp
    time.sleep(1)
    sendp(ack, iface=netface, verbose=1)
    print("ACK Packet sent")
    print(f"Ack gave {packet[BOOTP].yiaddr}")

# offer_pkt() - after we get the Discover packet from the client we create offer packet and send it back to the client,
# the offer packet will contain the possible IP that will be allocated ,subnet mask and other network configurations.
def offer_pkt(packet, netface):
    print("DISCOVER PACKET RECEIVED")
    mac = packet[BOOTP].chaddr
    transactionID = packet[BOOTP].xid
    ether = Ether(src=sender_mac, dst=mac)
    ip = IP(src=dhcp_fake_ip, dst="255.255.255.255")
    udp = UDP(sport=67, dport=68)
    bp = BOOTP(op=2, chaddr=packet[BOOTP].chaddr, yiaddr=newip, siaddr=dhcp_fake_ip, xid=transactionID)
    dhcp = DHCP(options=[("message-type", "offer"),
                         ("subnet_mask", "255.255.255.0"),
                         ("lease-time", 1600),
                         ("requested_addr", newip),
                         'end'])
    offer = ether / ip / udp / bp / dhcp
    time.sleep(1)
    sendp(offer, iface=netface, verbose=1)
    print("OFFER Packet sent")


if __name__ == "__main__":
    netface = get_iface()
    print("DHCP SERVER ON....")
    while True:
        pkt = sniff(iface=netface, filter="udp and (port 67 or 68)", count=1)[0]
        time.sleep(1)
        newip = get_ip()
        if pkt[DHCP].options[0][1] == 1:  # Discover
            offer_pkt(pkt, netface)
        elif pkt[DHCP].options[0][1] == 3:  # Request
            ack_pkt(pkt, netface)
        else:
            print("ERROR")
        time.sleep(1)
