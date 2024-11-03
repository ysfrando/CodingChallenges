import socket
import threading
import signal
import sys
from typing import List, Set

class ThreadedTCPServer:
    def __init__(self, host: str = '127.0.0.1', port: int = 8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
        self.clients: Set[socket.socket] = set() # Thread safe set of client sockets
        self.clients_lock = threading.Lock()
        self.running = True # Control flag for server shutdown

        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def start(self):
        """Start the server and listen for connections"""
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Server listening on {self.host}:{self.port}")

            while self.running:
               try:
                    client_socket, client_addr = self.server_socket.accept()
                    print(f"New connection from {client_addr}")
                    # Start a new thread for client
                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_addr))
                    client_thread.daemon = True
                    client_thread.start()
               except socket.error as e:
                    if not self.running:
                        break
                    print(f"Error accepting connection: {e}")

        except Exception as e:
            print(f"Server Error: {e}")
        finally:
            self.clean_up()
        
    def handle_client(self, client_socket: socket.socket, address: tuple):
        """Handle individual client connections"""
        try:
            with client_socket:
                with self.clients_lock:
                    self.clients.add(client_socket)
                while self.running:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    self.broadcast(data, sender=client_socket)
        
        except socket.error as e:
            print(f"Client {address} error: {e}")
        finally:
            with self.clients_lock:
                self.clients.discard(client_socket)
            print(f"Connection from {address} closed")
    
    def broadcast(self, message: bytes, sender: socket.socket):
        """Send message to all clients except sender"""
        with self.clients_lock:
            for client in self.clients:
                if client != sender:
                    try:
                        client.send(message)
                    except socket.error as e:
                        print(f"Error broadcasting to client: {e}")

    def shutdown(self, signum=None, frame=None):
        "Gracefully shutting down the server"
        self.running = False
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.connect((self.host, self.port))
            except socket.error:
                pass

    def clean_up(self):
        """Clean up server resources"""
        with self.clients_lock:
            for client in self.clients:
                try:
                    client.close()
                except socket.error:
                    pass
            self.clients.clear()
        self.server_socket.close()
        print("Server shutdown complete")

if __name__ == "__main__":
    server = ThreadedTCPServer()
    server.start()
