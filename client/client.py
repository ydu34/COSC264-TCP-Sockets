"""
Author: Yu Duan 
Date: 18/08/19
A TCP client accepts three parameters, the server IP address, the port number,
and the filename to retrieve from the server. 
"""

import socket
import sys
import os

def create_FileRequest_header(FileRequest_filename ):
    """ Creates the FileRequest header to send to server"""
    MagicNo = 0x497E
    MagicNo_byte1 = MagicNo >> 8
    MagicNo_byte2 = MagicNo & 0xFF
    Type = 0x1
    FileNameLen = len(FileRequest_filename)
    FileNameLen_byte1 = FileNameLen >> 8
    FileNameLen_byte2 = FileNameLen & 0xFF
    FileRequest_header = bytearray([MagicNo_byte1,
                                    MagicNo_byte2,
                                    Type,
                                    FileNameLen_byte1,
                                    FileNameLen_byte2]) 
    return FileRequest_header


# Intial parameter request 
if len(sys.argv) != 4:
    print("Please input three parameters, host, port number, and filename")
    sys.exit(1)

HOST = sys.argv[1]
PORT = sys.argv[2]
filename = sys.argv[3]


# Convert hostname to IP address
try: 
    HOST = socket.gethostbyname(HOST)
except socket.gaierror:
    print("The given hostname or IP address does not exist or not known")
    sys.exit(1)


# Check port number is betweem 1024 and 64000 (including)
try:
    PORT = int(PORT)
except ValueError:
    print("The port number must be between 1024 and 64000 (including)")
    sys.exit(1)

if PORT < 1024 or PORT > 64000:
    print("The port number must be between 1024 and 64000 (including)")
    sys.exit(1)


# Check if the file already exist locally.
if os.path.isfile(filename):
    print("The file already exists locally")
    sys.exit(1)


# Create the socket
try:
    sock = socket.socket()
    sock.settimeout(1) 
except socket.error: 
    print("Socket could not be created")
    sys.exit(1)


# Connects to the server using the IP address and port number
try:
    sock.connect((HOST, PORT))
except socket.error: 
    sock.close()
    print("Cannot connect with the server")
    sys.exit(1)


# Convert filename which is a string into byte array
FileRequest_filename  = filename.encode('utf-8')


# FileRequest header
FileRequest_header = create_FileRequest_header(FileRequest_filename)


# Send FileRequest header to server
try:
    sock.send(FileRequest_header)
except socket.error:
    print("Failed to send header")
    sock.close()
    sys.exit(1)    


# Send FileRequeset filename to server
try:
    sock.send(FileRequest_filename)
except socket.error:
    print("Failed to send filename")
    sock.close()
    sys.exit(1)    


# Recieve the FileResponse header from server
try:
    FileResponse_header = sock.recv(8)
except socket.timeout:
    print("The recieved FileResponse is erroneous, timeout exceeded")
    sock.close()
    sys.exit(1)
except socket.error:
    print("Cannot recieve a response from the server")
    sock.close()
    sys.exit(1) 
   
   
# Check the FileResponse Header 
try:
    FileResponse_MagicNo = (FileResponse_header[0] << 8) + FileResponse_header[1]
    FileResponse_Type = FileResponse_header[2]
    FileResponse_StatusCode = FileResponse_header[3]
    FileResponse_DataLength = (FileResponse_header[4] << 24) + (FileResponse_header[5] << 16) + (FileResponse_header[6] << 8) + FileResponse_header[7]   
except:
    print("The recieved FileResponse is erroneous, the header is incorrect")
    sock.close()
    sys.exit(1) 
     
if FileResponse_MagicNo != 0x497E or FileResponse_Type != 2 or FileResponse_StatusCode not in (0, 1):
    print("The recieved FileResponse is erroneous, the header is incorrect")
    sock.close()
    sys.exit(1)  
            

# This requested file does not exist on the server
if FileResponse_StatusCode == 0:
    print("There is no data for this file or the file does not exists on the server")
    sock.close()
    sys.exit(1) 


# The requested file does exists on the server
try:
    f = open(filename, "wb+")
except:
    print("The file cannot be opened for writing")
    sock.close()
    sys.exit(1)
  
    
# Loop for recieving data from the server and writting it to a file
number_bytes_recieved = 0
while True:
    try:
        FileResponse_data = sock.recv(4096)
        number_bytes_recieved += len(FileResponse_data)
        f.write(FileResponse_data)
        if not FileResponse_data:
            break
    except socket.timeout:
        print("The recieved data is errroneous, timeout exceeded")
        sock.close()
        f.close()
        sys.exit(1)
    except socket.error:
        print("The data cannot be fully recieved from the server")
        sock.close()
        f.close()
        sys.exit(1)            
    except:
        print("An error has occured writting the data to the file")
        sock.close()
        f.close()
        sys.exit(1)            
 
 
# Check that the bytes recieved matches the indicated amount        
if number_bytes_recieved != FileResponse_DataLength:
    print("The recieved data is erroneous, has less or more bytes than expected")
    sock.close()
    f.close()
    sys.exit(1)
    
    
print("The file has been recieved with a total of {} bytes".format(number_bytes_recieved))
f.close()
sock.close()
sys.exit(0)