import socket


class HTTPServer:
    def __init__(self, host="127.0.0.1", port=8080):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
    def start(self):
        """Start the server and listens for incoming connections."""
        try:
            # Bind the socket to the host and port
            self.server_socket.bind((self.host, self.port))
            print(f"Server started at {self.host}:{self.port}")
            
            # Listen for incoming connections
            self.server_socket.listen(5)
            print("Waiting for connections...")
            
            while True:
                client_socket, client_address = self.server_socket.accept()
                print(f"Connection from {client_address}")
                self.handle_client(client_socket)
                
        except Exception as e:
            print(f"Server error: {e}")
        finally:
            self.shutdown()
            
    
    def handle_client(self, client_socket):
        """Handles a client connection and return an HTTP response."""
        try:
            request = client_socket.recv(1024).decode('utf-8')
            print(f"Recieved request:\n{request}")
            
            if request:
                # Send an HTTP response with an HTML page
                response = self.generate_http_response()
                client_socket.sendall(response)
        
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
            
    
    def generate_http_response(self):
        """Generate a basic HTTP response with an HTML page."""
        html_content = """
        <html>
        <head><title>Sample Page</title></head>
        <body>
            <h1>Welcome to My HTTP Server</h1>
            <p>This is a simple web page served from Python.</p>
        </body>
        </html>
        """
        http_response = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(html_content)}\r\n"
            "Connection: close\r\n"
            "\r\n"
            f"{html_content}"
        )
        return http_response.encode('utf-8')
    
    
    def shutdown(self):
        """Shuts down the server."""
        self.server_socket.close()
        print("Server shut down...")

if __name__ == "__main__":
    server = HTTPServer(host="127.0.0.1", port=8080)
    server.start()
