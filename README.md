# COSC264-TCP-Sockets

This project was done for an assignment in the course COSC264 Introduction to Computer Networks and the Internet. 
This project consists of a server and an client which uses TCP sockets.The server is a command line application and will operate as a TCP server. In the same folder of the server, there will be files which the client can request the server for, essentially downloading a file from the server. The client is a command line application and will operate as a TCP client. The client may request a file from the server by filename, and the server will send the file to the client. The requested file will end up in the same folder as the client.

## How to run 

### Server
``` 
cd server
python server.py {port_number}
``` 
`{port_number}` the port the server will run on, it can be any number between 1024 and 64000 inclusive    

An example would be `python server.py 3000`

### Client
```
cd client   
python client.py {host_address} {port_number} {filename}
```  
`{host_address}` is the address that the server is hosted on. e.g localhost or 127.0. 0.1  
`{port_number}` is the port that the server is running on,  it can be any number between 1024 and 64000 inclusive  
`{filename}` is the file that the client wants to download from the server  

An example would be `python client.py localhost 3000 cat.jpeg`
