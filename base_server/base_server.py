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

# def server_tcp(host: str, port: int, fileserverip: str, fileserverport: int):
    # return
def rudp_server(host: str, port: int, fileserverip: str, fileserverport: int) -> None:
    # print("using rdup is wip")
    # socket(socket.AF_INET, socket.SOCK_STREAM)
    # (1) AF_INET is the address family for IPv4 (Address Family)
    # (2) SOCK_STREAM is the socket type for TCP (Socket Type) - [SOCK_DGRAM is the socket type for UDP]
    # Note: context manager ('with' keyword) closes the socket when the block is exited
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Prepare the server socket
        # * Fill in start (1)
        server_socket.bind((host, port))
        server_socket.listen()
        # * Fill in end (1)

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



    return


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
def tcp_httpsender(client_socket: socket.socket, client_address: tuple[str, int], fileserverip: str, fileserverport: int) -> None:
    print(f"{client_address[0]}:{client_address[1]} is requesting file")
    # process client request by turning it into a string
    processed_request = client_socket.recv(1024).decode('utf-8')
    if 'GET' in processed_request:
        # split the processed request and take the second value, which is the target of the GET request
        x = processed_request.split()
        print("get request is:")
        print(x)
        print()
        get_file_from_processed_request = x[1].split('/')
        # after splitting, the file is in 3rd elem
        file = get_file_from_processed_request[3]
        print(f"requested file is {file}")

        # no need to modify the redirected_url, need to get file from GET request
        redirected_url = f'http://{fileserverip}:{fileserverport}/{file}'
        redirection_request = requests.get(redirected_url)
        if redirection_request.status_code == 200:
            print("file is present on redirected server")
            
            # encoded_url = redirected_url.encode('utf-8')
            # redirected_url = redirected_url.encode('utf-8')
            # response_header = api.CalculatorHeader(int(time.time()), None, 000, False, False, 302, 0, (redirected_url.encode('utf-8')))
            # response_header = api.CalculatorHeader(int(time.time()), None, 000, False, False, False, 302, 0, redirected_url)
            response = f"302 /{file} HTTP/1.1 \r\nHost: {redirected_url} \r\nConnection: close\r\n\r\n"
            # packed_response = response_header.pack()
            # respone = response_header.pack()
            # print("response header is created")
            # redirected_url = redirected_url.pack()
            # client_socket.send(302)
            # client_socket.send_header('Content-Type', 'text/html')
            client_socket.sendall(response.encode('utf-8'))
            print("response sent")
            client_socket.close()
            print("socket closed")
            return
        else:
            response_404 = f"404 /{file} HTTP/1.1 \r\nHost: {redirected_url} \r\nConnection: close\r\n\r\n"
            '''
            TODO: create a 404 response and send to client, in case the requested file isn't available
            '''
            # print("file is not present, exiting.")
            client_socket.sendall(response_404.encode('utf-8'))
            print("file not present, 404 response sent.")
            client_socket.close()
            print("socket closed")
            return


# default server usage
def server(host: str, port: int, fileserverip: str, fileserverport: int) -> None:
    # socket(socket.AF_INET, socket.SOCK_STREAM)
    # (1) AF_INET is the address family for IPv4 (Address Family)
    # (2) SOCK_STREAM is the socket type for TCP (Socket Type) - [SOCK_DGRAM is the socket type for UDP]
    # Note: context manager ('with' keyword) closes the socket when the block is exited
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # Prepare the server socket
        # * Fill in start (1)
        server_socket.bind((host, port))
        server_socket.listen()
        # * Fill in end (1)

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






# this method decides what kind of connection to use
def input_handler(host: str, port: int, protocol: str, fileserverip: str, fileserverport: int) -> None:

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
    
        







# client handler
def client_handler(client_socket: socket.socket, client_address: tuple[str, int]) -> None:
    '''
    Function which handles client requests
    '''
    client_addr = f"{client_address[0]}:{client_address[1]}"
    client_prefix = f"{{{client_addr}}}"
    with client_socket:  # closes the socket when the block is exited
        print(f"Conection established with {client_addr}")
        while True:
            data = client_socket.recv(8192)
            # if data.ip == '127.0.0.2' and data.port == 8000

            if not data:
                break
            try:

                try:
                    request = api.CalculatorHeader.unpack(data)
                except Exception as e:
                    raise api.CalculatorClientError(
                        f'Error while unpacking request: {e}') from e

                print(f"{client_prefix} Got request of length {len(data)} bytes")

                response = process_request(request)

                response = response.pack()
                print(
                    f"{client_prefix} Sending response of length {len(response)} bytes")

                #Send the response back to the client
                client_socket.sendall(response)

            except Exception as e:
                print(f"Unexpected server error: {e}")
                client_socket.sendall(api.CalculatorHeader.from_error(
                    e, api.CalculatorHeader.STATUS_SERVER_ERROR, CACHE_POLICY, CACHE_CONTROL).pack())
            print(f"{client_prefix} Connection closed")



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
    # sending to filehandler
    input_handler(host, port, protocol, fileserverip, fileserverport)


    # file = 'test'
    # redirected_url = f'http://{fileserverip}:{fileserverport}/{file}'
    # print(redirected_url)
    # redirected_url = redirected_url.encode('utf-8')
    # print(redirected_url)
    #                                     (unix_time_stamp: int, total_length: typing.Optional[int], reserved: int, cache_result: bool, show_steps: bool, is_request: bool, status_code: int, cache_control: int, data: bytes = b'') -> None:
    # response_header = api.CalculatorHeader(int(time.time()), None, 000, False, False, False, 302, 0, redirected_url)
    

