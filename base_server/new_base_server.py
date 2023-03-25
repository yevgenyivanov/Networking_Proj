import numbers
import argparse
import socket
import socketserver
import threading
import http.server
import requests
import re
import api
import time
DEFAULT_SERVER_PORT = 8000
DEFAULT_SERVER_HOST = '127.0.0.1'
DEFAULT_PROTCOL = "TCP"
DEFAULT_FILESERVER_HOST = '127.0.0.2'
DEFAULT_FILESERVER_PORT = 8002

'''
Taken from https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/GET:
The HTTP GET method requests a representation of the specified resource. Requests using GET should only be used to request data (they shouldn't include data).

The example used for the following method was taken from https://developer.mozilla.org/en-US/docs/Glossary/Request_header:

GET /home.html HTTP/1.1
Host: developer.mozilla.org
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate, br
Referer: https://developer.mozilla.org/testpage.html
Connection: keep-alive
Upgrade-Insecure-Requests: 1
If-Modified-Since: Mon, 18 Jul 2016 02:36:04 GMT
If-None-Match: "c561c68d0ba92bbeb8b0fff2a9199f722e3a621a"
Cache-Control: max-age=0

As we clearly see, the GET is at the start of the request itself. This allows us to 
'''

# RUDP
def rudp_httpsender(server_socket: socket.socket, client_address: tuple[str, int], fileserverip: str, fileserverport: int, message: bytes) -> None:
    print(f"{client_address[0]}:{client_address[1]} is requesting file by rudp")
    # process client request by turning it into a string
    processed_request = message.decode('utf-8')
    if 'RUDP_GET' in processed_request:
        x = processed_request.split()
        print("Printing RUDP_GET request:")
        print(x)
        print()
        get_file_from_processed_request = x[1].split('/')
        # after splitting, the file is in 3rd elem
        file = get_file_from_processed_request[3]
        print(f"requested file is {file}")
        redirected_url = f'http://{fileserverip}:{fileserverport}/{file}'
        
        response = f"302 /{file} HTTP/1.1 \r\nHost: {redirected_url} \r\nConnection: close\r\n\r\n"
        
        server_socket.sendto(response.encode('utf-8'), client_address)
        print("response sent")
        server_socket.close()
        print("socket closed")
        
    return



# TCP
def tcp_httpsender(client_socket: socket.socket, client_address: tuple[str, int], fileserverip: str, fileserverport: int) -> None:
    print(f"{client_address[0]}:{client_address[1]} is requesting file")
    # process client request by turning it into a string
    processed_request = client_socket.recv(1024).decode('utf-8')
    if 'GET' in processed_request:
        # split the processed request and take the second value, which is the target of the GET request
        x = processed_request.split()
        print("Printing GET request:")
        print(x)
        print()
        get_file_from_processed_request = x[1].split('/')
        # after splitting, the file is in 3rd elem
        file = get_file_from_processed_request[3]
        print(f"requested file is {file}")

        
        redirected_url = f'http://{fileserverip}:{fileserverport}/{file}'
        
        response = f"302 /{file} HTTP/1.1 \r\nHost: {redirected_url} \r\nConnection: close\r\n\r\n"
        
        client_socket.sendall(response.encode('utf-8'))
        print("response sent")
        client_socket.close()
        print("socket closed")
    return

# default server usage
def server(host: str, port: int, fileserverip: str, fileserverport: int, protocol: str) -> None:
    # socket(socket.AF_INET, socket.SOCK_STREAM)
    # (1) AF_INET is the address family for IPv4 (Address Family)
    # (2) SOCK_STREAM is the socket type for TCP (Socket Type) - [SOCK_DGRAM is the socket type for UDP]
    
    #input handler:
    # tcp handler:
    if(protocol == DEFAULT_PROTCOL or protocol == 'TCP' or protocol == 'tcp'):
        print("Using default protocol, TCP")
        # set server_socket to tcp configuration
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Prepare the server socket
            server_socket.bind((host, port))
            server_socket.listen()
            # make thread array
            threads = []
            print(f"Listening on {host}:{port}")

            while True:
                try:
                    # Establish connection with client.
                    client_socket, address = server_socket.accept() 
                    

                    # Create a new thread to handle the client request
                    thread = threading.Thread(target=tcp_httpsender, args=(
                        client_socket, address, fileserverip, fileserverport))
                    thread.start()
                    threads.append(thread)
                except KeyboardInterrupt:
                    print("Shutting down...")
                    break

            for thread in threads:  # Wait for all threads to finish
                thread.join()
########################################################################################################################## 
##########################################################################################################################
##########################################################################################################
##########################################################################################################################
##########################################################################################################################    
    # handling rudp
    if(protocol == 'RUDP' or protocol == 'rudp'):
        print("Using non-default protocol, RUDP")
        # set server_socket to udp configuration
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
            server_socket.bind((host, port))
            # server_socket.listen()
            

            threads = []
            print(f"Listening on {host}:{port}")

            while True:
                try:
                    # Establish connection with client.

                    # need to fix: recvfrom() receives from the socket information but doesn't know how to process it
                    bytesAddressPair = server_socket.recvfrom(1024)
                    message = bytesAddressPair[0]
                    client_address = bytesAddressPair[1]
                    print(f"accepeted connection from {client_address[0]}:{client_address[1]}")
                    print(f"message: {message}")
                    
                    # Create a new thread to handle the client request
                    thread = threading.Thread(target=rudp_httpsender, args=(
                        server_socket, client_address, fileserverip, fileserverport, message))
                    thread.start()
                    threads.append(thread)
                except KeyboardInterrupt:
                    print("Shutting down...")
                    break
                    return
            return
    # Note: context manager ('with' keyword) closes the socket when the block is exited
    
    # handling unrelated procotol
    else:
        print("protocol is not supported, exiting.")
        return
        





# this method decides what kind of connection to use
def input_handler(host: str, port: int, fileserverip: str, fileserverport: int) -> None:

# hanlding tcp
    if(protocol == DEFAULT_PROTCOL or protocol == 'TCP' or protocol == 'tcp'):
        print("Using default protocol, TCP")
        # no special protocol was specified, send to default server usage
        server(host, port, fileserverip, fileserverport)
        return

# handling rudp
    if(protocol == 'RUDP' or protocol == 'rudp'):
        # send to rudp server 
        rudp_server(host, port, fileserverip, fileserverport)
        return
        # todo
        
# handling unrelated procotol
    else:
        print("protocol is not supported, exiting.")
        return
    
        




# main
if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='The Redirection Server.')

# default running param
    arg_parser.add_argument('-p', '--port', type=int,
                            default=DEFAULT_SERVER_PORT, help='The port to listen on.')
    arg_parser.add_argument('-H', '--host', type=str,
                            default=DEFAULT_SERVER_HOST, help='The host to listen on.')
    arg_parser.add_argument('-pr', '--protocol', type=str,
                            default=DEFAULT_PROTCOL, help='The protocol to use. Choose either UDP or TCP(default)')
    arg_parser.add_argument('-fs', '--fileserverip', type=str,
                            default=DEFAULT_FILESERVER_HOST, help='The file server ip.')
    arg_parser.add_argument('-fp', '--fileserverport', type=int,
                            default=DEFAULT_FILESERVER_PORT, help='The file server port.')
    args = arg_parser.parse_args()

    host = args.host
    port = args.port
    protocol = args.protocol
    fileserverip = args.fileserverip
    fileserverport = args.fileserverport
    # sending to server
    server(host, port, fileserverip, fileserverport, protocol)
    

