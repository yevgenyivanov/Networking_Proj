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

def exponential_growth()

def file_to_bytesArray_func(os_filesize: int, file_inbytes: bytes):
    elems_in_filedata_array = os_filesize / 1024
    # calculate remainder of the division above
    remainder = elems_in_filedata_array - int(elems_in_filedata_array)
    # create additional element for data that wasn't divided equally
    if remainder > 0:
        remainder = 1 
    file_bytes_array = []
    # if remainder was 0 the file was divided equally
    total_elems = int(elems_in_filedata_array)+ remainder
    # add the bytes data
    for i in range(total_elems):
        # print("current bytes: ", file_inbytes[(i*1024):((i+1)*1024)])
        file_bytes_array.append(
            file_inbytes[i*1024:(i+1)*1024]
        )
        print(file_bytes_array[i])
        # print("i is: ", i)
    return file_bytes_array

def congestion_control(client_socket: socket.socket, client_address: tuple[str, int], file_size: int, file_bytes_array):
    total_elems = len(file_bytes_array)
    counter=1
    print(len(file_bytes_array))
    # send i of bytes, encode a bytestream of (i)*1024):((2*(i+1))*1024)
    for i in range(len(file_bytes_array)):
        
        curr_byte_stream = file_bytes_array[
            (counter*i*1024):
            (i+1)*1024]
        # curr_stream_number = 
        
    return

# RUDP
def rudp_send(client_socket: socket.socket, client_address: tuple[str, int], message: bytes) -> None:
    processed_request = message.decode('utf-8')
    
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
            File Data Separation:
            * After calculating file size, divide the file into smaller fragments (arbitrary value of 1024bytes)
            if file_size/1024 - int(file_size/1024) > 0 --> not whole division so we add additional element to array
            * declare an array with size of the rounded value of file_size/1024(add 1 extra elem if needed)
            * insert the data into the array
            Done. Needs Testing.
            Testing Complete.

            TODO
            Congestion Control:
             Exponential growth in sending - in order to send exponential data size, (we'll set arbitrary value of 4096bytes)
              combine amount of data_elements until we reach 64,512bytes, exponentaily:
              if we sent 1024bytes, received an ACK next time we will send 2048bytes, then 4096bytes etc.
              (the previous amount of bytes sent X2)
              This will lead to a maximum of 1024*63 = 64512bytes being transferred at once
              (Note: Although the maximum UDP packet size is 65,507 for ipv4 we round it down)
              
             Linear decrease in sending - reduce the amount of data from 64,512bytes by 2048bytes for each ACK
              so if we reached maximum UDP threshold we keep reducing amound of bytes sent.
              from 64,512 to 62,464 to 62,464 etc. all the way to 3/4 of 64,512 = 48,384bytes being sent.
              Then re-enter the loop of adding 1024bytes Exponentially
            
            TODO
            Flow Control:
             If we exceed the 65,507 / 2 = 32,753.5bytes, the client will send a PAUSE packet request. 
             This packet will cause a halt of 25-45ms in data transfer (sleep), and then continue the loop
        '''



        if get_file_from_processed_request == 'file.txt':
            
            
            file_size = None
            file_bytes_array = None
            with open('hosted_files/file.txt', 'rb') as file:
                    file_size = os.path.getsize('hosted_files/file.txt')
                    file_bytes = file.read()
                    print("file is read in bytes to bytes")
                    file_bytes_array = file_to_bytesArray_func(file_size, file_bytes)
                    print("len of file_bytes_array: ", len(file_bytes_array))
            
            # if file_bytes_array != None:
            #     print("file_bytes_array created successfully")
                    
            
            # send file size using sendto
            # client_socket.sendto(str(file_size).encode('utf-8'), client_address)
            # print("data size sent")
            congestion_control(client_socket, client_address, file_size, file_bytes_array)

            # client_socket.sendall(response)
            # client_socket.close()
            # print("socket closed")
            return

        



        if get_file_from_processed_request == 'file2.txt':
            print("processed response from ")
            
            file_size = None
            with open('hosted_files/file2.txt', 'rb') as file:
                    file_size = os.path.getsize('hosted_files/file2.txt')
                    response = file.read()
                    print("file is converted to bytes, sending")

            # send file size
            client_socket.send(str(file_size).encode('utf-8'))
            # print("data size sent")
            # client_socket.sendall(response)
            # client_socket.close()
            # print("socket closed")
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
            client_socket.send(str(file_size).encode('utf-8'))
            # print("data size sent")
            # client_socket.sendall(response)
            # client_socket.close()
            # print("socket closed")
            return

        else:
            response = ("404_NOT_FOUND").encode('utf-8')
            client_socket.send(response)
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
            

            threads = []
            print(f"Listening on {host}:{port}")

            while True:
                try:
                    # Establish connection with client.
                    # client_socket, address = server_socket.accept() 
                    bytesAddressPair = server_socket.recvfrom(1024)
                    message = bytesAddressPair[0]
                    address = bytesAddressPair[1]
                    print(f"accepeted connection from {address}")

                    # Create a new thread to handle the client request
                    thread = threading.Thread(target=rudp_send, args=(
                        server_socket, address, message))
                    thread.start()
                    threads.append(thread)
                except KeyboardInterrupt:
                    print()
                    print("Shutting down...")
                    break

            # for thread in threads:  # Wait for all threads to finish
            #     thread.join()
            # return
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
