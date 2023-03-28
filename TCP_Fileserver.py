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
import time

DEFAULT_SERVER_HOST = '127.0.0.2'
DEFAULT_SERVER_PORT = 2060
DEFAULT_PROTOCOL = "TCP"


# convert file a bytes array
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

        if get_file_from_processed_request == 'file_tcp.txt':
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

        if get_file_from_processed_request == 'image_tcp.jpg':
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
            time.sleep(1)
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


def tcp_file_server():
    print(f"TCP Fileserver...")
    # set server_socket to tcp configuration
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Prepare the server socket
        server_socket.bind((DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT))
        server_socket.listen()
        # make thread array
        threads = []
        print(f"Listening on {DEFAULT_SERVER_HOST}:{DEFAULT_SERVER_PORT}")

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


# main
if __name__ == '__main__':
    # sending to file_server
    tcp_file_server()
