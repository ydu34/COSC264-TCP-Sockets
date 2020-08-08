"""
Author: Yu Duan 
Date: 18/08/19
A TCP server that accepts one parameter, the port number from the command line.
"""

import socket
import sys
import datetime
import os

def create_FileResponse_header(StatusCode=0, DataLength=0x0):
    """Creates the FileResponse header to send back to the client"""
    MagicNo = 0x497E
    MagicNo_byte1 = MagicNo >> 8
    MagicNo_byte2 = MagicNo & 0xFF 
    Type = 0x2
    DataLength_byte1 = DataLength >> 24
    DataLength_byte2 = (DataLength >> 16) & 0xFF
    DataLength_byte3 = (DataLength >> 8) & 0xFF
    DataLength_byte4 = DataLength & 0xFF
   
    FileResponse_header = bytearray([MagicNo_byte1,
                                     MagicNo_byte2, 
                                     Type, 
                                     StatusCode, 
                                     DataLength_byte1, 
                                     DataLength_byte2,
                                     DataLength_byte3, 
                                     DataLength_byte4])
    return FileResponse_header


if len(sys.argv) != 2:
    print("Please input one parameter, port number")
    sys.exit(1)
      
HOST = '0.0.0.0'
PORT = sys.argv[1]


# Check that the port number is between 1,024 and 64,000 (including)
try:
    PORT = int(PORT)
except ValueError:
    print("The port number must be between 1024 and 64000 (including)")
    sys.exit(1)

if PORT < 1024 or PORT > 64000:
    print("The port number must be between 1,024 and 64,000 (includig)")
    sys.exit(1)
    
    
# Create the socket and bind to the socket
try:
    sock = socket.socket()
    sock.bind((HOST, PORT))
except socket.error:
    print("Failed to create/bind the socket")
    sys.exit(1)


# Listen on the socket 
try:
    sock.listen()
except: 
    print("The server cannot listen on the socket")
    sock.close()
    sys.exit(1)

    
# The server enters a infinite loop 
while True:
    # Accept the incoming connection
    try:
        client_sock, ip_addr = sock.accept()       
        client_sock.settimeout(1) 
        print("Current time: {}".format(datetime.datetime.now().time())) 
        print("Accepted connection from: {}". format(ip_addr))  
    except socket.error:
        print("Failed to accept incomming connection")
        continue

    
    # Recieve the FileRequest header into a byte array
    try:
        FileRequest_header = client_sock.recv(5)
    except socket.timeout:
        print("The recieved FileRequest is errroneous, timeout exceeded")
        client_sock.close()
        continue
    
    
    # Check the FileRequest header for errors
    try:
        MagicNo = (FileRequest_header[0] << 8) + FileRequest_header[1]
        FileRequest_Type = FileRequest_header[2]
        FileNameLen = (FileRequest_header[3] << 8) + FileRequest_header[4]
    except:
        print("The recieved FileRequest is errroneous, the header is incorrect")
        client_sock.close()
        continue   
    
    if MagicNo != 0x497E or FileRequest_Type != 1 or FileNameLen < 1 or FileNameLen > 1024:
        print("The recieved FileRequest is errroneous, the header is incorrect")
        client_sock.close()
        continue     
        
        
    # Recieve the FileRequest data into a byte array
    try:
        filename = client_sock.recv(1024)
    except socket.timeout:
        print("The recieved FileRequest is errroneous, timeout exceeded")
        client_sock.close()
        continue


    # Check if FileRequest data has correct number of bytes
    if FileNameLen != len(filename):
        print("The recieved FileRequest is errroneous, incorrect number of bytes in data")
        client_sock.close()
        continue

    
    # Open the file for reading 
    try:
        f = open(filename.decode('utf-8'), "rb")
        StatusCode = 1       
    except OSError:
        print("The requested file does not exists or cannot be opened for reading")
        StatusCode = 0
        FileResponse_header = create_FileResponse_header(StatusCode)
        client_sock.send(FileResponse_header)        
        client_sock.close()
        continue
    
    DataLength = os.path.getsize(os.getcwd() + "/" + filename.decode('utf-8'))
    FileResponse_header = create_FileResponse_header(StatusCode, DataLength)
    
    
    # Send FileResponse header with StatusCode 1 if file can be opened for reading
    try:
        client_sock.send(FileResponse_header) 
    except:
        print("Failed to send file response to the client")
        client_sock.close()
        continue
    
    
    # Send the file data
    try:
        bytes_sent = 0
        while True:
            file_data = f.read(4096)
            client_sock.send(file_data)
            bytes_sent += len(file_data)        
            if not file_data:
                break
    except:
        print("Failed to send file data to the client")
        f.close()
        client_sock.close()
        continue
        
        
    f.close()
    client_sock.close()
    print("The file has been transfered with a total of {} bytes".format(bytes_sent))