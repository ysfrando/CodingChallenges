import socket

def tcp_client(host: str = '127.0.0.1', port: int = 8080):
    # Create a socket for the client
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the server
        client_socket.connect((host, port))
        print(f"Connected to server at {host}:{port}")

        # Send data to the server
        message = "Hello, Server!"
        client_socket.sendall(message.encode('utf-8'))
        print(f"Sent: {message}")

        # Optionally, receive a response from the server
        response = client_socket.recv(1024)
        print(f"Received from server: {response.decode('utf-8')}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()
        print("Client socket closed")

if __name__ == "__main__":
    tcp_client()
