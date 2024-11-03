import socket


def tcp_server(host="127.0.0.1", port=8080):
    # Init a TCP socket object
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)

    while True:
        client_socket, client_addr = server_socket.accept()
        print(f"Client connection from: {client_addr}")
        
        data = client_socket.recv(1024)
        if data:
            client_socket.send(data)
        client_socket.close()

if __name__ == "__main__":
    tcp_server()
