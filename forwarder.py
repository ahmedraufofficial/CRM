import socket
import threading

# Configuration
SERVER_HOST = '0.0.0.0'  # Listen on all network interfaces
SERVER_PORT = 9090       # Port on your VPS server
DEST_IP = '192.168.0.19'  # Destination IP on your local network
DEST_PORT = 8085          # Port on 192.168.0.19

def handle_client(client_socket):
    # Connect to the destination server
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.connect((DEST_IP, DEST_PORT))
    
    # Forwarding loop
    while True:
        # Receive data from the client
        client_data = client_socket.recv(4096)
        if not client_data:
            break
        # Forward received data to the server
        server_socket.sendall(client_data)
        
        # Receive data from the server
        server_data = server_socket.recv(4096)
        if not server_data:
            break
        # Forward received data back to the client
        client_socket.sendall(server_data)
    
    # Close sockets
    client_socket.close()
    server_socket.close()

def main():
    # Create a socket to accept incoming connections
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_HOST, SERVER_PORT))
    server_socket.listen(5)
    print(f"[*] Listening on {SERVER_HOST}:{SERVER_PORT}")

    try:
        while True:
            client_socket, client_addr = server_socket.accept()
            print(f"[*] Accepted connection from {client_addr[0]}:{client_addr[1]}")
            
            # Handle each client connection in a separate thread
            client_thread = threading.Thread(target=handle_client, args=(client_socket,))
            client_thread.start()
    
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
    
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()