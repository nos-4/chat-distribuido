import socket
import threading
from datetime import datetime

# Configurações do servidor
HOST = '127.0.0.1'
PORT = 55555

# Criação do socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

clients = []
usernames = {}

def broadcast(message, sender=None):
    for client in clients:
        if client != sender:  # <- NÃO envia para quem enviou
            try:
                client.send(message.encode('utf-8'))
            except:
                clients.remove(client)

def handle_client(client):
    username = usernames[client]

    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                raise Exception("Cliente desconectado")
            print(f"[{datetime.now().strftime('%H:%M:%S')}] {username}: {message}")
            broadcast(f"{username}: {message}", sender=client)  # envia apenas para os outros
        except:
            clients.remove(client)
            del usernames[client]
            client.close()
            broadcast(f"SISTEMA: {username} saiu do chat.", sender=None)
            print(f"{username} desconectado.")
            break

def receive_connections():
    print(f"Servidor iniciado em {HOST}:{PORT}")
    print("Aguardando conexões...\n")

    while True:
        client, address = server.accept()
        client.send("Digite seu nome de usuário: ".encode('utf-8'))
        username = client.recv(1024).decode('utf-8').strip()

        while username in usernames.values():
            client.send("Nome já em uso. Escolha outro: ".encode('utf-8'))
            username = client.recv(1024).decode('utf-8').strip()

        usernames[client] = username
        clients.append(client)

        print(f"Novo usuário conectado: {username} ({address})")
        client.send(f"Bem-vindo ao chat, {username}!".encode('utf-8'))
        broadcast(f"SISTEMA: {username} entrou no chat!", sender=client)

        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

if __name__ == "__main__":
    receive_connections()
