import socket
import argparse 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('hostname', help='the IP Address Of Proxy Server')
    parser.add_argument('port', help='the port number of the proxy server')
    args = parser.parse_args()
    proxyHost = args.hostname
    proxyPort = int(args.port)
    
    clientSocket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    clientSocket.settimeout(10)
    
    try:
        clientSocket.connect((proxyHost,proxyPort))
    
        while True:
            try:
                sentence = input("Enter input:")
                clientSocket.send(sentence.encode())
                modifiedSentence = clientSocket.recv(1024).decode()
                print(f"Server returned: {modifiedSentence}")
                if (modifiedSentence == "ReceivedExit"):
                    clientSocket.close()
                    return
            except socket.error as e:
                print(f"Error in sending/receiving data: {e}")
            except KeyboardInterrupt:
                print("\nUser interrupted the process. Closing connection...")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break
            
    except socket.timeout:
        print("Connection timed out")
    except ConnectionRefusedError:
        print("Connection failed. The server may not be running or the address/port is incorrect.")
    except socket.error as e:
        print(f"Socket error occurred: {e}")
    except Exception as e:
        print(f"Unexpected error during connection: {e}")
    finally:
        # Ensure the socket is always closed
        print("Closing connection.")
        clientSocket.close()

if __name__ == "__main__":
    main()