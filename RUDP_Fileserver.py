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

DEFAULT_SERVER_HOST = '127.0.0.3'
DEFAULT_SERVER_PORT = 3247
DEFAULT_PROTCOL = "RUDP"




# helper funcs



# conver file a bytes array
def file_to_bytesArray_func(os_filesize: int, file_inbytes: bytes):
    elems_in_filedata_array = os_filesize / 1024
    # calculate remainder of the division above
    remainder = elems_in_filedata_array - int(elems_in_filedata_array)
    # create additional element for data that wasn't divided equally
    if remainder > 0:
        remainder = 1
    file_bytes_array = []
    # if remainder was 0 the file was divided equally
    total_elems = int(elems_in_filedata_array) + remainder
    # add the bytes data
    for i in range(total_elems):
        file_bytes_array.append(
            file_inbytes[i * 1024:(i + 1) * 1024]
        )
    return file_bytes_array




# ack control
def ack_control(server_socket: socket.socket, client_address: tuple[str, int], current_packet:bytes):
    ack_response = server_socket.recv(1024).decode('utf-8')
    if f"NO_ACK_" in ack_response:
        # split response
        server_socket.sendto(current_packet, client_address)
        # i = ack_response.split("_")[2]
        # resent i range of file_bytes_array:
        # for j in range(i):
            # (range_start, range_end) in enumerate(exponential_growth(1,2))

        return
        
# exponential growth for packet sending
def exponential_growth(previous_max: int, exponential_growth_rate: int):
    current_min = previous_max
    while True:
        yield (current_min, current_min * exponential_growth_rate)
        current_min *= exponential_growth_rate


def linear_decline(previous_max:int, decline_rate:int):
    current_max = previous_max
    while True:
        yield(current_max, decline_rate)
        current_max = current_max - decline_rate
        decline_rate += decline_rate
        

# add bytes to send as string
def byte_addition(file_bytes_array, start:int, end:int):
    
    byte_stream = b''
    for i in range(start, end):
        byte_stream += file_bytes_array[i]
    return byte_stream




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
              combine amount of data_elements until we reach 63,488bytes, exponentaily:
              if we sent 1024bytes, received an ACK next time we will send 2048bytes, then 4096bytes etc.
              (the previous amount of bytes sent X2)
              This will lead to a maximum of 1024*62 = 63,488bytes being transferred at once
              (Note: Although the maximum UDP packet size is 65,507 for ipv4 we round it down)

             Linear decrease in sending - reduce the amount of data from 63,488bytes by 2048bytes for each ACK
              so if we reached maximum UDP threshold we keep reducing amound of bytes sent.
              from 63,488 to 62,464 to 62,464 etc. all the way to 3/4 of 63,488 = 47,616bytes being sent.
              Then re-enter the loop of adding 1024bytes Exponentially

            TODO
            Flow Control:
             If we exceed the 65,507 / 2 = 32,753.5bytes, the client will send a PAUSE packet request. 
             This packet will cause a halt of 25-45ms in data transfer (sleep), and then continue the loop
'''



# congestion control
def congestion_control(server_socket: socket.socket, client_address: tuple[str, int], file_size: int, file_bytes_array):
    # amount of 1024 bytes elements in file_bytes_array
    total_elems = len(file_bytes_array)
    max_bytes_amount = 0
    
    # send file size
    server_socket.sendto(str(file_size).encode('utf-8'), client_address)
    print("sent filesize: ", total_elems)

    # receive SEND_ELEMS to send total amount of elements expected
    send_response = server_socket.recv(1024).decode('utf-8')
    if "SEND_ELEMS" in send_response:
        server_socket.sendto(str(total_elems).encode('utf-8'), client_address)
        print("sent total elems: ", total_elems)
    else:
        print("not SEND_ELEMS quitting")
        return
    
    # waiting for send_file_bytes request
    send_response = server_socket.recv(1024).decode('utf-8')
    if "SEND_FILE_BYTES_ARRAY" in send_response:
        print("received SEND_FILE_BYTES_ARRAY ", send_response)
        
    # send first 1024 bytes
        current_packet = byte_addition(file_bytes_array, 0, 1)
        server_socket.sendto(current_packet, client_address)
        # waiting for ack
        ack_control(server_socket, client_address, current_packet)
    
    else:
        print("Not SEND_FILE_BYTES_ARRAY, qutting")
        return
    
    # i will be packet number out of total_elems
    for i, (range_start, range_end) in enumerate(exponential_growth(1,2)):
        
        
        # break condition for sending all packets before reaching max congestion window size
        if i == total_elems:
            current_packet = byte_addition(file_bytes_array, range_start, range_end)
            server_socket.sendto(current_packet, client_address)
            max_bytes_amount = i
            server_socket.sendto('END_OF_FILE'.encode('utf-8'), client_address)
            print()
            break
        
        
        
        # break condition for reaching max congestion window size
        if i == 5:
            # sent 32-62 array elements of file_bytes_array
            current_packet = byte_addition(file_bytes_array, range_start, 62)
            server_socket.sendto(current_packet, client_address)
            ack_control(server_socket, client_address, current_packet)
            max_bytes_amount = 62
            print()
            break

        # continue iterating till max congestion window size, using ack_control after each packet sent
        current_packet = byte_addition(file_bytes_array, range_start, range_end)
        server_socket.sendto(current_packet, client_address)
        print(f"               Bytes_Range_Start: {range_start}, Bytes_Range_End: {range_end}")
        print(f"Iteration {i+1}, Bytes_Sent_Start: {(range_start)*1024}, Bytes_Sent_End: {1024*(range_end)}")
        ack_control(server_socket, client_address, current_packet)
        max_bytes_amount=range_end
        print()
    
    if max_bytes_amount == total_elems:
        return
    




    # linear decline
    # start from max bytes_amount to continute where we left off
    for i, (max_bytes_amount, range_end ) in enumerate(linear_decline(max_bytes_amount, 2)):
        if i == total_elems:
            current_packet = byte_addition(file_bytes_array, range_start, max_bytes_amount-1)
            server_socket.sendto(current_packet, client_address)
            print(f"               Bytes_Range_Start: {max_bytes_amount}, Bytes_Range_End: {max_bytes_amount + range_end}")
            print(f"Iteration {i+1}, Bytes_Sent_Start: {range_start*1024}, Bytes_Sent_End: {1024*(range_start+ range_end)}") # 1024*62 =
            ack_control(server_socket, client_address, current_packet) 
            break
        
        # send until reaching end of file_to_bytesArray
        current_packet = byte_addition(file_bytes_array, range_start, range_start+(range_start - range_end))
        server_socket.sendto(current_packet, client_address)
        print(f"               Bytes_Range_Start: {max_bytes_amount}, Bytes_Range_End: {max_bytes_amount + range_end}")
        print(f"Iteration {i+1}, Bytes_Sent_Start: {max_bytes_amount*1024}, Bytes_Sent_End: {1024*(max_bytes_amount+range_end)}") # 1024*62 = 
        ack_control(server_socket, client_address, current_packet)
    return


# RUDP
def rudp_send(server_socket: socket.socket) -> None:
    bytesAddressPair = server_socket.recvfrom(1024)
    message = bytesAddressPair[0]
    address = bytesAddressPair[1]
    print(f"accepeted connection from {address}")
    client_address = (address[0], #host
                      int(address[1])) #port
    processed_request = message.decode('utf-8')

    if 'RUDP_GET_FILE' in processed_request:
        x = processed_request.split()
        print("Printing RUDP_GET_FILE request:")
        print(x)
        print()
        get_file_from_processed_request = x[1].split('/')[3]
        # checking the if a file that's requested is among the hosted_files/
        print("requested file is: ", get_file_from_processed_request)


        if get_file_from_processed_request == 'file_udp.txt':
            file_size = None
            file_bytes_array = None
            with open('hosted_files/file.txt', 'rb') as file:
                file_size = os.path.getsize('hosted_files/file.txt')
                file_bytes = file.read()
                print("file is read in bytes to bytes")
                file_bytes_array = file_to_bytesArray_func(file_size, file_bytes)
                print("len of file_bytes_array: ", len(file_bytes_array))

            congestion_control(server_socket, client_address, file_size, file_bytes_array)
            return

        if get_file_from_processed_request == 'image_udp.jpg':
            file_size = None
            file_bytes_array = None

            with open('hosted_files/image_1.jpg', 'rb') as file:
                file_size = os.path.getsize('hosted_files/image_1.jpg')
                print("file_size: ", file_size)
                file_bytes = file.read()
                print("file is read in bytes to bytes")
                file_bytes_array = file_to_bytesArray_func(file_size, file_bytes)
                print("len of file_bytes_array: ", len(file_bytes_array))
                
            
            congestion_control(server_socket, client_address, file_size, file_bytes_array)


        else:
            response = ("404_NOT_FOUND").encode('utf-8')
            server_socket.send(response)
            server_socket.close()

        return


    else:
        print("not RUDP_GET_FILE request. returning")
        return


# TCP

def rudp_file_server() -> None:
    print(f"RUDP Fileserver...")
    # set server_socket to udp configuration
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as server_socket:
        # SO_REUSEADDR is a socket option that allows the socket to be bound to an address that is already in use.
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        server_socket.bind((DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT))
        print(f"RUDP Fileserver listening on {DEFAULT_SERVER_HOST}:{DEFAULT_SERVER_PORT}...")
        
        rudp_send(server_socket)


# main
if __name__ == '__main__':
    # sending to file_server
    rudp_file_server()