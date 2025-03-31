# Include the libraries for socket and system calls
import socket
import sys
import os
import argparse
import re

# 1MB buffer size
BUFFER_SIZE = 1000000

# Get the IP address and Port number to use for this web proxy server
parser = argparse.ArgumentParser()
parser.add_argument('hostname', help='the IP Address Of Proxy Server')
parser.add_argument('port', help='the port number of the proxy server')
args = parser.parse_args()
proxyHost = args.hostname
proxyPort = int(args.port)

# Create a server socket, bind it to a port and start listening
try:
  # Create a server socket
  # ~~~~ INSERT CODE ~~~~
  serverSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
  # ~~~~ END CODE INSERT ~~~~
  print ('Created socket')
except:
  print ('Failed to create socket')
  sys.exit()

try:
  # Bind the the server socket to a host and port
  # ~~~~ INSERT CODE ~~~~
  serverSocket.bind((proxyHost, proxyPort))
  # ~~~~ END CODE INSERT ~~~~
  print ('Port is bound')
except:
  print('Port is already in use')
  sys.exit()

try:
  # Listen on the server socket
  # ~~~~ INSERT CODE ~~~~
  serverSocket.listen(1)
  # ~~~~ END CODE INSERT ~~~~
  print ('Listening to socket')
except:
  print ('Failed to listen')
  sys.exit()

# continuously accept connections
while True:
  print ('Waiting for connection...')
  # Accept connection from client and store in the clientSocket
  try:
    # ~~~~ INSERT CODE ~~~~
    clientSocket = None
    clientSocket, addr = serverSocket.accept()
    # ~~~~ END CODE INSERT ~~~~
    print ('Received a connection')
  except:
    print ('Failed to accept connection')
    sys.exit()
  # Get HTTP request from client
  # and store it in the variable: message_bytes
  # ~~~~ INSERT CODE ~~~~
  message_bytes = clientSocket.recv(BUFFER_SIZE)
  # ~~~~ END CODE INSERT ~~~~
  message = message_bytes.decode('utf-8')
  print ('Received request:')
  print ('< ' + message)
  # Extract the method, URI and version of the HTTP client request 
  requestParts = message.split()
  method = requestParts[0]
  URI = requestParts[1]
  version = requestParts[2]
  print ('Method:\t\t' + method)
  print ('URI:\t\t' + URI)
  print ('Version:\t' + version)
  print ('')
  # Get the requested resource from URI
  # Remove http protocol from the URI
  URI = re.sub('^(/?)http(s?)://', '', URI, count=1)
  # Remove parent directory changes - security
  URI = URI.replace('/..', '')
  # Split hostname from resource name
  resourceParts = URI.split('/', 1)
  hostname = resourceParts[0]
  resource = '/'
  if len(resourceParts) == 2:
    # Resource is absolute URI with hostname and resource
    resource = resource + resourceParts[1]
  print ('Requested Resource:\t' + resource)
  #Check if resource is in cache
  try:
    cacheLocation = './' + hostname + resource
    if cacheLocation.endswith('/'):
        cacheLocation = cacheLocation + 'default'
    print ('Cache location:\t\t' + cacheLocation)
    # default
    fileExists = os.path.isfile(cacheLocation) 
    
    # modification
    # if not os.path.isfile(cacheLocation):
    #   print("Not a file")
    
    # Check whether the file is currently in the cache
    cacheFile = open(cacheLocation,'r')
    cacheData = cacheFile.readlines()
    print ('Cache hit! Loading from cache file: ' + cacheLocation)
    # ProxyServer finds a cache hit
    # Send back response to client 
    # ~~~~ INSERT CODE ~~~~
    response = ''.join(cacheData)
    response.replace('\n','\r\n')
    cacheData = response
    clientSocket.send(response.encode())
    # ~~~~ END CODE INSERT ~~~~
    cacheFile.close()
    print ('Sent to the client:')
    print ('> ' + cacheData)
  except:
    # cache miss.  Get resource from origin server
    originServerSocket = None
    # Create a socket to connect to origin server
    # and store in originServerSocket
    # ~~~~ INSERT CODE ~~~~
    originServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # ~~~~ END CODE INSERT ~~~~
    print ('Connecting to:\t\t' + hostname + '\n')
    try:
      # Get the IP address for a hostname
      address = socket.gethostbyname(hostname)
      # Connect to the origin server
      # ~~~~ INSERT CODE ~~~~
      originServerSocket.connect((address, 80))
      # ~~~~ END CODE INSERT ~~~~
      print ('Connected to origin Server')
      originServerRequest = ''
      originServerRequestHeader = ''
      # Create origin server request line and headers to send
      # and store in originServerRequestHeader and originServerRequest
      # originServerRequest is the first line in the request and
      # originServerRequestHeader is the second line in the request
      # ~~~~ INSERT CODE ~~~~
      originServerRequest = f"{method} {resource} {version}\r\n"
      originServerRequestHeader += f"Host: {hostname}\r\n\r\n"
      # ~~~~ END CODE INSERT ~~~~
      # Construct the request to send to the origin server
      request = originServerRequest + originServerRequestHeader
      # Request the web resource from origin server
      print ('Forwarding request to origin server:')
      for line in request.split('\r\n'):
        print ('> ' + line)
      try:
        originServerSocket.sendall(request.encode())
      except socket.error:
        print ('Forward request to origin failed')
        sys.exit()
      print('Request sent to origin server\n')
      # Get the response from the origin server
      # ~~~~ INSERT CODE ~~~~
      # try:
      #   # Receive the response in chunks
      #   response = b''  # Initialize an empty byte string to store the response
  
      #   while True:
      #       chunk = originServerSocket.recv(1024)  # Receive data in chunks
      #       if not chunk:  # If no more data is received, exit the loop
      #         break
      #       response += chunk  # Append the chunk to the response
      #   # Convert the response bytes to a string (assuming it's text-based, like HTTP)
      #   response_str = response.decode('utf-8')
      #   print('Response received from origin server:')
      #   print(response_str)
      # except Exception as e:
      #   print(f'Error receiving response from origin server: {e}')
      #   sys.exit()
      try:
        response = originServerSocket.recv(BUFFER_SIZE)
      except Exception as e:
          print(f'Error receiving response from origin server: {e}')
          sys.exit()
      # ~~~~ END CODE INSERT ~~~~
      # Send the response to the client
      # ~~~~ INSERT CODE ~~~~
      
      response_str = response.decode('utf-8')
      response_lines = response_str.split("\r\n")
      status_line = response_lines[0]
      
      status_code = int(status_line.split(" ")[1])
      
      for line in response_lines:
        if line.lower().startswith("cache-control:"):
          cache_control = line.split(":", 1)[1].strip()
          break

          
        # if location:
        #   print("New location:", location)
        #   location = re.sub('^(/?)http(s?)://', '', location, count=1)
        #   location = location.replace('/..', '')
        #   redirectedResourceParts = location.split('/', 1)
        #   hostname = redirectedResourceParts[0]
        #   redirectedResource = '/'
        #   if len(redirectedResourceParts) == 2:
        #     # Resource is absolute URI with hostname and resource
        #     redirectedResource = redirectedResource + redirectedResourceParts[1]
          
      try:
        clientSocket.sendall(response)  # Send the response to the client (as bytes)
        print('Response sent to the client\n')
      except Exception as e:
        print(f'Error sending response to client: {e}')
        sys.exit()
      # ~~~~ END CODE INSERT ~~~~
      # Create a new file in the cache for the requested file.
      if status_code not in (301, 302) or cache_control == "no-store":
        cacheDir, file = os.path.split(cacheLocation)
        print ('cached directory ' + cacheDir)
        if not os.path.exists(cacheDir):
          os.makedirs(cacheDir)
        cacheFile = open(cacheLocation, 'wb')
        # Save origin server response in the cache file
        # ~~~~ INSERT CODE ~~~~
        cacheFile.write(response)  # Write the raw response bytes to the cache file
        # ~~~~ END CODE INSERT ~~~~
        cacheFile.close()
        print('cache file closed')
      # finished communicating with origin server - shutdown socket writes
      print('origin response received. Closing sockets')
      originServerSocket.close()
      
      clientSocket.shutdown(socket.SHUT_WR)
      print ('client socket shutdown for writing')
    except OSError as err:
      print ('origin server request failed. ' + err.strerror)
  try:
    clientSocket.close()
  except:
    print ('Failed to close client socket')