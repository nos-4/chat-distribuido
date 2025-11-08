import socket
import threading
from datetime import datetime
from colorama import Fore, Style, init

# Inicializa o colorama
init(autoreset=True)

# Configurações do servidor
HOST = '127.0.0.1'  # localhost
PORT = 55555

# Criação do socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()

# Listas de controle
clients = []
usernames = {}

# Função para broadcast de mensagens
def broadcast(message, sender=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {message}"
    for client in clients:
        try:
            client.send(formatted_msg.encode('utf-8'))
        except:
            clients.remove(client)

# Função para lidar com mensagens de um cliente
def handle_client(client):
    username = usernames[client]

    while True:
        try:
            message = client.recv(1024).decode('utf-8')
            if not message:
                raise Exception("Cliente desconectado")
            
            # Exibe mensagem no terminal do servidor
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"{Fore.CYAN}[{timestamp}] {Fore.YELLOW}{username}: {Fore.WHITE}{message}")

            # Envia a mensagem para todos os outros
            broadcast(f"{username}: {message}", sender=client)
        except:
            # Cliente desconectou
            clients.remove(client)
            del usernames[client]
            client.close()
            broadcast(f"{Fore.RED}{username} saiu do chat.{Style.RESET_ALL}")
            print(f"{Fore.RED}{username} desconectado.")
            break

# Função principal de conexão
def receive_connections():
    print(f"{Fore.GREEN}Servidor iniciado em {HOST}:{PORT}")
    print(f"{Fore.BLUE}Aguardando conexões...\n")

    while True:
        client, address = server.accept()

        # Login de usuário (recebe nome)
        client.send("Digite seu nome de usuário: ".encode('utf-8'))
        username = client.recv(1024).decode('utf-8').strip()

        # Verifica se o nome já está em uso
        while username in usernames.values():
            client.send("Nome já em uso. Escolha outro: ".encode('utf-8'))
            username = client.recv(1024).decode('utf-8').strip()

        # Armazena e adiciona cliente à lista
        usernames[client] = username
        clients.append(client)

        print(f"{Fore.GREEN}Novo usuário conectado: {Fore.YELLOW}{username} {Fore.WHITE}({address})")
        client.send(f"Bem-vindo ao chat, {username}!\n".encode('utf-8'))
        broadcast(f"{Fore.MAGENTA}{username} entrou no chat!{Style.RESET_ALL}")

        # Cria thread para esse cliente
        thread = threading.Thread(target=handle_client, args=(client,))
        thread.start()

# Execução do servidor
if __name__ == "__main__":
    receive_connections()
