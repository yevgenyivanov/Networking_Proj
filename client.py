import urllib.request
from io import BytesIO
from PIL import Image
import requests
import argparse
import socket
import sys
# Define the IP address and port number of the server
DEFAULT_SERVER_HOST = '127.0.0.1'
DEFAULT_SERVER_PORT = 8000
DEFAULT_PROTOCOL = 'TCP'
# Define the path to the file you want to download on the server
DEFAULT_FILENAME = 'file.txt'
# file_path = '/file2.txt'

# Construct the URL to the file
file_url = f'http://{DEFAULT_SERVER_HOST}:{DEFAULT_SERVER_PORT}/{DEFAULT_FILENAME}'
def noop():
    pass
# Download the file
# urllib.request.urlretrieve(file_url, 'file_saved.txt')
# urllib.request.urlretrieve(file_url, 'file_saved2.txt')

def client(server_address: tuple[str, int], filename: str, protocol: str) -> None:
    # server_prefix = f"{{{server_address[0]}:{server_address[1]}}}"
    
    # use tcp
    if(protocol == DEFAULT_PROTOCOL or protocol == 'TCP' or protocol == 'tcp'):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect(server_address)
            # establishing connection

            print(f"Connection established. Requesting file {filename}")
            file_separated = filename.split('.')
            try:
                file_url = f'http://{server_address[0]}:{server_address[1]}/{filename}'
                print("created file url.")

                request = f"GET {file_url} HTTP/1.1 \r\nHost: {server_address[0]} \r\nConnection: open \r\n\r\n"
                # send initial GET
                client_socket.sendall(request.encode('utf-8'))
                print("sent get request")
                # receive GET response
                response = client_socket.recv(1024).decode('utf-8')
                print("received response")
                
                # check if 302 is received in response to initial GET
                if '302' in response:
                    print("received 302")
                    print(f"printing decoded response: \n{response}")
                    print()
                    response = response.split(' ')
                    print("printing split response: ")
                    print(response)
                    print()
                    print("requesting file from redirected server")
                    print()
                    redirected_host = response[4].split('/')[2]
                    # redirected_port = response[4].split('/')[3]
                    print(f"redirected_host: {redirected_host}")
                    # create new url from 302
                    redirected_file_url = f'http://{redirected_host}/{filename}'
                    
                    print("Final url ", redirected_file_url)
                    print()
                    # connect to new server
                    client_socket.close()
                    print("socket closed")
                    new_host = str(redirected_host.split(':')[0])
                    new_port = int(redirected_host.split(':')[1])

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
                        request = f"GET_FILE {redirected_file_url} HTTP/1.1 \r\nHost: {server_address[0]} \r\nConnection: open \r\n\r\n"
                        print("GET_FILE request: ", request)
                        
                        new_client_socket.send(request.encode('utf-8'))

                        # receive file_size in bytes
                        file_size = new_client_socket.recv(8192).decode('utf-8')
                        print("file size is: " ,file_size)
                        print()
                        file_size_tracker = 0
                        response = b''
                        while file_size_tracker <= int(file_size):
                            response = response + new_client_socket.recv(8192)
                            print("sizeof response: ", int(sys.getsizeof(response)))
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
    



















    # use rudp
    if(protocol == 'RUDP' or protocol == 'rudp'):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
            client_socket.connect(server_address)
            # establishing connection
            
            print(f"Connection established. Requesting file {filename}")
            file_separated = filename.split('.')
            try:
                file_url = f'http://{server_address[0]}:{server_address[1]}/{filename}'
                print("created file url.")

                request = f"RUDP_GET {file_url} HTTP/1.1 \r\nHost: {server_address[0]} \r\nConnection: open \r\n\r\n"
                # send initial GET
                client_socket.sendall(request.encode('utf-8'))
                print("sent get request")
                # receive GET response
                response = client_socket.recv(1024).decode('utf-8')
                print("received response")
                
                # check if 302 is received in response to initial GET
                if '302' in response:
                    print("received 302")
                    print(f"printing decoded response: \n{response}")
                    print()
                    response = response.split(' ')
                    print("printing split response: ")
                    print(response)
                    print()
                    print("requesting file from redirected server")
                    print()
                    redirected_host = response[4].split('/')[2]
                    # redirected_port = response[4].split('/')[3]
                    print(f"redirected_host: {redirected_host}")
                    # create new url from 302
                    redirected_file_url = f'http://{redirected_host}/{filename}'
                    
                    print("Final url ", redirected_file_url)
                    print()
                    # connect to new server
                    client_socket.close()
                    print("socket closed")
                    new_host = str(redirected_host.split(':')[0])
                    new_port = int(redirected_host.split(':')[1])

                    print("new host: ", new_host)
                    print("new port: ", new_port)
                    print()
                    server_address = (new_host, new_port)

                    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as new_client_socket:
                        new_client_socket.connect(server_address)

                        # server_address = (new_host, int(new_port))
                        
                        # client_socket.connect((new_host, new_port))
                        print("socket reconntected to new server")
                        # send GET_FILE request
                        request = f"RUDP_GET_FILE {redirected_file_url} HTTP/1.1 \r\nHost: {server_address[0]} \r\nConnection: open \r\n\r\n"
                        print("RUDP_GET_FILE request: ", request)
                        
                        new_client_socket.send(request.encode('utf-8'))

                        # receive file_size in bytes
                        file_size = new_client_socket.recv(8192).decode('utf-8')
                        print("file size is: " ,file_size)
                        print()
                        file_size_tracker = 0
                        response = b''
                        while file_size_tracker <= int(file_size):
                            response = response + new_client_socket.recv(8192)
                            print("sizeof response: ", int(sys.getsizeof(response)))
                            file_size_tracker = int(sys.getsizeof(response))

                        saved_filename = filename.split('.')[0] + '_saved'
                        saved_filename_extenstion = filename.split('.')[1]
                        with open(f'{saved_filename}.{saved_filename_extenstion}', 'wb') as file:
                                file.write(response)
                                print("file written correctly")
                        
                        print("file received(finally!)")
                        return
                else:
                    print("File not present on server. Exiting")
                    return
            except Exception as e:
                print(f"{server_address} Unexpected error: {str(e)}")
        print(f"{server_address} Connection closed")


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description="A Calculator Client.")

    arg_parser.add_argument("-H", "--host", type=str,
                            default=DEFAULT_SERVER_HOST, help="The host to connect to.")
    arg_parser.add_argument("-p", "--port", type=int,
                            default=DEFAULT_SERVER_PORT, help="The port to connect to.")
    arg_parser.add_argument("-f", "--file", type=str,
                            default=DEFAULT_FILENAME, help="The file to retrieve.")
    arg_parser.add_argument("-pr", "--protocol", type=str,
                            default=DEFAULT_PROTOCOL, help="The protocol to use in order to retrieve the file.")

    args = arg_parser.parse_args()

    host = args.host
    port = args.port
    filename = args.file
    protocol = args.protocol
    client((host, port), filename, protocol)
    