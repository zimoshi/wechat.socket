import socket
import threading
import argparse

# Global list of clients and names
clients = {}

# Server function
def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print("Starting server....")
    
    def handle_client(client_socket, addr):
        name = client_socket.recv(1024).decode('utf-8')
        clients[client_socket] = name
        broadcast(f"{name} has joined the chat!", client_socket)
        print(f"{name} joined from {addr}")
        
        while True:
            try:
                message = client_socket.recv(1024).decode('utf-8')
                if message == "__TYPING__":
                    broadcast(f"{name} is typing...", client_socket, exclude_self=True)
                    continue
                if not message:
                    break
                broadcast(f"{name}: {message}", client_socket)
            except ConnectionResetError:
                break
        
        print(f"{name} disconnected")
        broadcast(f"{name} has left the chat.", client_socket)
        del clients[client_socket]
        client_socket.close()
    
    def broadcast(message, sender_socket, exclude_self=False):
        for client, client_name in clients.items():
            if exclude_self and client == sender_socket:
                continue
            try:
                client.send(message.encode('utf-8'))
            except:
                pass
    
    while True:
        try:
            client_socket, addr = server.accept()
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.start()
        except:
            print("Closing server...")
            break

# Client function
def start_client(host, port):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((host, port))
    
    name = input("Name: ")
    client.send(name.encode("utf-8"))
    print(f"\nJoining server on {host}:{port}....")
    
    def receive_messages():
        while True:
            try:
                message = client.recv(1024).decode('utf-8')
                if not message:
                    break
                print(message)
            except ConnectionResetError:
                break
    
    recv_thread = threading.Thread(target=receive_messages)
    recv_thread.start()
    
    while True:
        msg = input("Message: ")
        if msg.lower() == "exit":
            break
        elif msg == "":
            client.send("__TYPING__".encode("utf-8"))
        else:
            client.send(msg.encode("utf-8"))
    
    client.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="WeChat Socket")
    parser.add_argument("-p", "--port", type=int, default=6789, help="Port number")
    parser.add_argument("-s", "--server", action="store_true", help="Start as server")
    
    args = parser.parse_args()
    host = "localhost"
    
    if args.server:
        start_server(host, args.port)
    else:
        start_client(host, args.port)
