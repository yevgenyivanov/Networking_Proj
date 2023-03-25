import http.server
import socketserver
from pathlib import Path
from io import BytesIO
from PIL import Image
import os
import socket
import threading
import argparse
import http.server
import requests
DEFAULT_SERVER_HOST = '127.0.0.2'
DEFAULT_SERVER_PORT = 8002
DEFAULT_PROTCOL = "TCP"




# RUDP
def rudp_send(client_socket: socket.socket, client_address: tuple[str, int]) -> None:
    processed_request = client_socket.recv(1024).decode('utf-8')
    
    if 'RUDP_GET_FILE' in processed_request:
        x = processed_request.split()
        print("Printing RUDP_GET_FILE request:")
        print(x)
        print()
        get_file_from_processed_request = x[1].split('/')[3]
        # checking the if a file that's requested is among the hosted_files/
        print("requested file is: ", get_file_from_processed_request)


            '''
            TODO
            After calculating file size, divide the file into smaller fragments (arbitrary value of 1024bytes)
            if file_size/1024 - int(file_size/1024) > 0 --> not whole division so we add additional element to array
            declare an array with size of the rounded value of file_size/1024(add 1 if needed)
            
            '''

        if get_file_from_processed_request == 'file.txt':
            print("processed response from ")
            
            file_size = None
            with open('hosted_files/file.txt', 'rb') as file:
                    file_size = os.path.getsize('hosted_files/file.txt')
                    response = file.read()
                    print("file is converted to bytes, sending")
            
            # send file size
            client_socket.sendall(str(file_size).encode('utf-8'))
            print("data size sent")
            client_socket.sendall(response)
            client_socket.close()
            print("socket closed")
            return

        
        if get_file_from_processed_request == 'file2.txt':
            print("processed response from ")
            
            file_size = None
            with open('hosted_files/file2.txt', 'rb') as file:
                    file_size = os.path.getsize('hosted_files/file2.txt')
                    response = file.read()
                    print("file is converted to bytes, sending")

            # send file size
            client_socket.sendall(str(file_size).encode('utf-8'))
            print("data size sent")
            client_socket.sendall(response)
            client_socket.close()
            print("socket closed")
            return

        
        if get_file_from_processed_request == 'image_1.jpg':
            print("processed response from ")
            
            file_size = None
            with open('hosted_files/image_1.jpg', 'rb') as file:
                    file_size = os.path.getsize('hosted_files/image_1.jpg')
                    print("file_size: ", file_size)
                    response = file.read()
                    print("file is converted to bytes, sending")

            # send file size
            client_socket.sendall(str(file_size).encode('utf-8'))
            print("data size sent")
            client_socket.sendall(response)
            client_socket.close()
            print("socket closed")
            return

        else:
            response = ("404_NOT_FOUND").encode('utf-8')
            client_socket.sendall(response)
            client_socket.close()

        return
    
    
    else:
        print("not RUDP_GET_FILE request. returning")
        return






# TCP
def tcp_send(client_socket: socket.socket, client_address: tuple[str, int]) -> None:
    
    processed_request = client_socket.recv(1024).decode('utf-8')
    
    if 'GET_FILE' in processed_request:
        x = processed_request.split()
        print("Printing GET_FILE request:")
        print(x)
        print()
        get_file_from_processed_request = x[1].split('/')[3]
        # checking the if a file that's requested is among the hosted_files/
        print("requested file is: ", get_file_from_processed_request)

        if get_file_from_processed_request == 'file.txt':
            print("processed response from ")
            
            file_size = None
            with open('hosted_files/file.txt', 'rb') as file:
                    file_size = os.path.getsize('hosted_files/file.txt')
                    response = file.read()
                    print("file is converted to bytes, sending")

            # send file size
            client_socket.sendall(str(file_size).encode('utf-8'))
            print("data size sent")
            client_socket.sendall(response)
            client_socket.close()
            print("socket closed")
            return

        
        if get_file_from_processed_request == 'file2.txt':
            print("processed response from ")
            
            file_size = None
            with open('hosted_files/file2.txt', 'rb') as file:
                    file_size = os.path.getsize('hosted_files/file2.txt')
                    response = file.read()
                    print("file is converted to bytes, sending")

            # send file size
            client_socket.sendall(str(file_size).encode('utf-8'))
            print("data size sent")
            client_socket.sendall(response)
            client_socket.close()
            print("socket closed")
            return

        
        if get_file_from_processed_request == 'image_1.jpg':
            print("processed response from ")
            
            file_size = None
            with open('hosted_files/image_1.jpg', 'rb') as file:
                    file_size = os.path.getsize('hosted_files/image_1.jpg')
                    print("file_size: ", file_size)
                    response = file.read()
                    print("file is converted to bytes, sending")

            # send file size
            client_socket.sendall(str(file_size).encode('utf-8'))
            print("data size sent")
            client_socket.sendall(response)
            client_socket.close()
            print("socket closed")
            return

        else:
            response = ("404_NOT_FOUND").encode('utf-8')
            client_socket.sendall(response)
            client_socket.close()

        return
    
    
    else:
        print("not GET_FILE request. returning")
        return















def file_server(host: str, port: int, protocol: str) -> None:
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
                    print(f"accepeted connection from {address}")

                    # Create a new thread to handle the client request
                    thread = threading.Thread(target=tcp_send, args=(
                        client_socket, address))
                    thread.start()
                    threads.append(thread)
                except KeyboardInterrupt:
                    print()
                    print("Shutting down...")
                    break

            for thread in threads:  # Wait for all threads to finish
                thread.join()
            return




    # handling rudp
    if(protocol == 'RUDP' or protocol == 'rudp'):
        print("Using non-default protocol, RUDP")
        # set server_socket to udp configuration
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
            server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
            server_socket.bind((host, port))
            server_socket.listen()
            

            threads = []
            print(f"Listening on {host}:{port}")

            while True:
                try:
                    # Establish connection with client.
                    client_socket, address = server_socket.accept() 
                    print(f"accepeted connection from {address}")

                    # Create a new thread to handle the client request
                    thread = threading.Thread(target=rudp_send, args=(
                        client_socket, address))
                    thread.start()
                    threads.append(thread)
                except KeyboardInterrupt:
                    print()
                    print("Shutting down...")
                    break

            for thread in threads:  # Wait for all threads to finish
                thread.join()
            return
    # Note: context manager ('with' keyword) closes the socket when the block is exited
    
    # handling unrelated procotol
    else:
        print("protocol is not supported, exiting.")
        return
    

# main
if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(
        description='The Redirection Server.')
# default running param
    arg_parser.add_argument('-H', '--host', type=str,
                            default=DEFAULT_SERVER_HOST, help='The host to listen on.')
    arg_parser.add_argument('-p', '--port', type=int,
                            default=DEFAULT_SERVER_PORT, help='The port to listen on.')
    arg_parser.add_argument('-pr', '--protocol', type=str,
                            default=DEFAULT_PROTCOL, help='The protocol to use. Choose either UDP or TCP(default)')
    
    args = arg_parser.parse_args()

    host = args.host
    port = args.port
    protocol = args.protocol
    
    # sending to file_server
    file_server(host, port, protocol)
