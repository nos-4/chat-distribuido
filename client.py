import socket
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# ----- Funções do chat -----
def receive_messages():
    while True:
        try:
            msg = client.recv(1024).decode("utf-8")
            display_message(msg)
        except:
            messagebox.showerror("Erro", "Conexão perdida com o servidor.")
            client.close()
            break

def send_message():
    msg = message_entry.get()
    if msg.strip() != "":
        client.send(msg.encode("utf-8"))
        display_message(f"{username}: {msg}", own=True)
        message_entry.delete(0, tk.END)

def display_message(msg, own=False):
    chat_box.configure(state='normal')
    if msg.startswith("SISTEMA:"):
        chat_box.insert(tk.END, msg + "\n", 'system')
    elif own:
        chat_box.insert(tk.END, msg + "\n", 'own')
    else:
        chat_box.insert(tk.END, msg + "\n", 'other')
    chat_box.configure(state='disabled')
    chat_box.yview(tk.END)

# ----- Login -----
def login_window():
    global username_entry, login_screen
    login_screen = tk.Tk()
    login_screen.title("Login - Chat Distribuído")
    login_screen.geometry("300x150")
    login_screen.configure(bg="#f5f5f5")

    tk.Label(login_screen, text="Digite seu nome de usuário:", bg="#f5f5f5").pack(pady=10)
    username_entry = tk.Entry(login_screen)
    username_entry.pack(pady=5)
    tk.Button(login_screen, text="Entrar", command=attempt_login, bg="#a2d5f2").pack(pady=10)

    login_screen.mainloop()

def attempt_login():
    global username
    username = username_entry.get().strip()
    if username == "":
        messagebox.showwarning("Aviso", "Insira um nome de usuário válido!")
        return
    try:
        client.send(username.encode("utf-8"))
        response = client.recv(1024).decode("utf-8")
        if "Nome já em uso" in response:
            messagebox.showerror("Erro", "Nome já está em uso. Tente outro!")
            return
        login_screen.destroy()
        open_chat()
    except:
        messagebox.showerror("Erro", "Não foi possível conectar ao servidor.")

# ----- Janela do chat -----
def open_chat():
    global chat_box, message_entry
    chat_window = tk.Tk()
    chat_window.title(f"Chat - {username}")
    chat_window.geometry("500x400")
    chat_window.configure(bg="#f5f5f5")

    # Chat box com scroll
    global chat_box
    chat_box = scrolledtext.ScrolledText(chat_window, width=60, height=20, state='disabled', bg="#ffffff")
    chat_box.pack(pady=10, padx=10)

    # Tags para cores
    chat_box.tag_config('own', foreground="#0000ff")
    chat_box.tag_config('other', foreground="#008000")
    chat_box.tag_config('system', foreground="#ff0000", font=("Arial", 10, "italic"))

    # Campo de entrada e botão
    frame_entry = tk.Frame(chat_window, bg="#f5f5f5")
    frame_entry.pack(pady=5)
    message_entry = tk.Entry(frame_entry, width=40)
    message_entry.pack(side=tk.LEFT, padx=5)
    send_button = tk.Button(frame_entry, text="Enviar", command=send_message, bg="#a2d5f2")
    send_button.pack(side=tk.LEFT)

    threading.Thread(target=receive_messages, daemon=True).start()
    chat_window.mainloop()

# ----- Conexão ao servidor -----
HOST = "127.0.0.1"
PORT = 55555
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

welcome_msg = client.recv(1024).decode("utf-8")

login_window()
