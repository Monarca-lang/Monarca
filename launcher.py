import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import os
import subprocess
import sys
import threading
import webbrowser
import json

CONFIG_PATH = "config.json"
DEFAULT_CONFIG = {
    "tema": "escuro",
    "last_file": None
}

# Carrega config
if os.path.exists(CONFIG_PATH):
    with open(CONFIG_PATH, "r") as f:
        config = json.load(f)
else:
    config = DEFAULT_CONFIG.copy()

def salvar_config():
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f)

TEMAS = {
    "escuro": {
        "left_panel_bg": "#2e2e3e",
        "button_bg": "#3a3a5a",
        "button_fg": "#ffffff",
        "terminal_bg": "#000000",
        "terminal_fg": "#ffffff"
    },
    "claro": {
        "left_panel_bg": "#e0e0e0",
        "button_bg": "#cfcfcf",
        "button_fg": "#000000",
        "terminal_bg": "#ffffff",
        "terminal_fg": "#000000"
    }
}

BASE_DIR = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))

processo = None

# Usamos TkinterDnD.Tk ao invés de tk.Tk para suportar drag and drop
root = TkinterDnD.Tk()
root.title("Launcher Monarca")
root.geometry("1235x600")
root.minsize(800, 500)

style = ttk.Style(root)
style.theme_use('clam')

def aplicar_tema():
    tema_cores = TEMAS[config["tema"]]
    style.configure("My.TFrame", background=tema_cores["left_panel_bg"])
    style.configure("TButton", background=tema_cores["button_bg"], foreground=tema_cores["button_fg"], font=("Segoe UI", 12), padding=6)
    style.map("TButton",
              background=[("active", "#6ea0f6"), ("!active", tema_cores["button_bg"])],
              foreground=[("active", "white"), ("!active", tema_cores["button_fg"])])

    terminal_frame.config(bg=tema_cores["terminal_bg"])
    terminal_output.config(bg=tema_cores["terminal_bg"], fg=tema_cores["terminal_fg"], insertbackground=tema_cores["terminal_fg"])
    input_entry.config(bg=tema_cores["terminal_bg"], fg=tema_cores["terminal_fg"], insertbackground=tema_cores["terminal_fg"])
    ultimos_label.config(bg=tema_cores["left_panel_bg"], fg=tema_cores["button_fg"])
    info_label.config(bg=tema_cores["left_panel_bg"], fg=tema_cores["button_fg"])
    label_versao_interpretador.config(bg=tema_cores["left_panel_bg"], fg=tema_cores["button_fg"])
    label_versao_launcher.config(bg=tema_cores["left_panel_bg"], fg=tema_cores["button_fg"])
    logo_container.config(bg=tema_cores["left_panel_bg"])
    logo_label.config(bg=tema_cores["left_panel_bg"])

painel_esquerdo = ttk.Frame(root, style="My.TFrame")
painel_esquerdo.pack(side="left", fill="y")

frame_controle = ttk.Frame(painel_esquerdo, style="My.TFrame")
frame_controle.pack(side="top", fill="both", expand=True, padx=10, pady=10)

terminal_frame = tk.Frame(root)
terminal_frame.pack(side="right", fill="both", expand=True, padx=5, pady=5)

terminal_output = tk.Text(terminal_frame, font=("Consolas", 11), wrap="none", borderwidth=0, highlightthickness=0)
terminal_output.pack(fill="both", expand=True, side="top", padx=(0, 0), pady=(5, 5))

scrollbar = ttk.Scrollbar(terminal_frame, orient="vertical", command=terminal_output.yview)
scrollbar.pack(side="right", fill="y", pady=(5, 5))
terminal_output.config(yscrollcommand=scrollbar.set)

input_entry = tk.Entry(terminal_frame, font=("Consolas", 11))
input_entry.pack(fill="x", side="bottom", padx=(0, 0), pady=(0, 5))

def enviar_input(event=None):
    texto = input_entry.get()
    if processo and processo.stdin:
        try:
            terminal_output.insert("end", texto + "\n")
            terminal_output.see("end")
            processo.stdin.write(texto + "\n")
            processo.stdin.flush()
        except Exception as e:
            print("Erro ao enviar input:", e)
    input_entry.delete(0, tk.END)

input_entry.bind("<Return>", enviar_input)

def abrir_arquivo_mc():
    path = filedialog.askopenfilename(filetypes=[("Arquivos Monarca", "*.mc")])
    if path:
        abrir_arquivo(path)

def abrir_arquivo(path):
    if path and path.lower().endswith(".mc"):
        config["last_file"] = os.path.abspath(path)
        atualizar_arquivo_atual(path)
        executar_script(config["last_file"])
        salvar_config()
        input_entry.focus_set()
    else:
        messagebox.showerror("Erro", "Por favor, selecione um arquivo '.mc' válido.")

def ler_stream(stream):
    global processo
    while True:
        char = stream.read(1)
        if char == "" and processo.poll() is not None:
            break
        if char:
            terminal_output.insert("end", char)
            terminal_output.see("end")

def executar_script(arquivo):
    global processo
    if not arquivo:
        messagebox.showwarning("Aviso", "Nenhum arquivo selecionado.")
        return

    terminal_output.delete("1.0", "end")

    main_py_path = os.path.join(BASE_DIR, "main.py")
    arg_arquivo = os.path.basename(arquivo)

    processo = subprocess.Popen(
        [sys.executable, main_py_path, "-s", arg_arquivo],
        cwd=BASE_DIR,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.PIPE,
        universal_newlines=True,
        bufsize=1
    )

    threading.Thread(target=ler_stream, args=(processo.stdout,), daemon=True).start()
    threading.Thread(target=ler_stream, args=(processo.stderr,), daemon=True).start()

def reexecutar_script():
    if config.get("last_file") and os.path.exists(config["last_file"]):
        executar_script(config["last_file"])
        input_entry.focus_set()
    else:
        messagebox.showwarning("Aviso", "Nenhum arquivo foi executado anteriormente para re-executar.")

def parar_execucao():
    global processo
    if processo and processo.poll() is None:
        try:
            processo.terminate()
            processo = None
            terminal_output.insert("end", "\n[Execução interrompida]\n")
            terminal_output.see("end")
        except Exception as e:
            terminal_output.insert("end", f"\n[Erro ao interromper o processo: {e}]\n")
            terminal_output.see("end")

def atualizar_arquivo_atual(arquivo):
    config["last_file"] = arquivo
    ultimos_label.config(text=f"Arquivo atual:\n{os.path.basename(arquivo)}")

def abrir_documentacao():
    webbrowser.open_new_tab("https://github.com/Monarca-lang/Monarca/blob/main/Documenta%C3%A7%C3%A3o.md")

def alternar_tema():
    config["tema"] = "claro" if config["tema"] == "escuro" else "escuro"
    salvar_config()
    aplicar_tema()

def criar_botao(texto, comando):
    btn = ttk.Button(frame_controle, text=texto, command=comando)
    btn.pack(pady=6, ipadx=10)
    return btn

ultimos_label = tk.Label(frame_controle, text="Arquivo atual:\n(nenhum)", font=("Segoe UI", 12, "bold"), justify="left")
ultimos_label.pack(fill="x", pady=(0, 10))

info_label = tk.Label(frame_controle, text="Informações da linguagem Monarca:", font=("Segoe UI", 12), justify="left")
info_label.pack(fill="x", pady=(0, 0))

# Subtextos com informações adicionais
versao_interpretador = "Versão do interpretador: nem perto de produção" #+ sys.version.split()[0]
versao_launcher = "Versão do Launcher: 0.6.9"  # Pode pegar dinamicamente se tiver como

label_versao_interpretador = tk.Label(frame_controle, text=versao_interpretador, font=("Segoe UI", 9), justify="left")
label_versao_interpretador.pack(fill="x", padx=5, pady=(2, 0))

label_versao_launcher = tk.Label(frame_controle, text=versao_launcher, font=("Segoe UI", 9), justify="left")
label_versao_launcher.pack(fill="x", padx=5, pady=(0, 10))

def mostrar_tutorial():
    tutorial_text = (
        "Bem-vindo ao Launcher Monarca!\n\n"
        "1. Use o botão 'Selecionar arquivo .MC' para escolher um arquivo Monarca (.mc) do seu computador.\n"
        "2. O conteúdo do arquivo será executado e a saída aparecerá no terminal à direita.\n"
        "3. Você pode digitar comandos ou entradas no campo abaixo do terminal e pressionar Enter para enviá-los ao programa.\n"
        "4. Para interromper a execução, clique em 'Parar execução'.\n"
        "5. Arraste e solte arquivos .mc na área lateral para abri-los rapidamente.\n"
        "6. Use 'Alternar tema' para mudar entre tema claro e escuro.\n"
        "7. Clique em 'Abrir documentação' para acessar a documentação online.\n"
        "\nDica: O arquivo atual é mostrado no topo do painel lateral.\n"
    )
    messagebox.showinfo("Tutorial - Como usar o Launcher Monarca", tutorial_text)

btn_tutorial = criar_botao("Tutorial", mostrar_tutorial)
btn_mc = criar_botao("Selecionar arquivo .MC", abrir_arquivo_mc)
btn_reexecutar = criar_botao("Re-executar último", reexecutar_script)
btn_parar_exec = criar_botao("Parar execução", parar_execucao)
btn_doc = criar_botao("Abrir documentação", abrir_documentacao)
btn_tema = criar_botao("Alternar tema", alternar_tema)

# LOGO
logo_container = tk.Frame(painel_esquerdo)
logo_container.pack(side="bottom", fill="both", expand=True, pady=10)

# Debounce helper for logo resizing
class Debounce:
    def __init__(self, func, wait=100):
        self.func = func
        self.wait = wait
        self._after_id = None

    def __call__(self, *args, **kwargs):
        if self._after_id:
            root.after_cancel(self._after_id)
        self._after_id = root.after(self.wait, lambda: self.func(*args, **kwargs))

try:
    logo_path = os.path.join(BASE_DIR, "logo.png")
    logo_img_raw = Image.open(logo_path)

    def redimensionar_logo():
        largura = painel_esquerdo.winfo_width()
        altura = int(painel_esquerdo.winfo_height() * 0.4)
        if largura and altura:
            proporcao_original = logo_img_raw.width / logo_img_raw.height
            largura_alvo = int(altura * proporcao_original)
            if largura_alvo > largura:
                largura_alvo = largura
                altura = int(largura_alvo / proporcao_original)
            img = logo_img_raw.copy().resize((largura_alvo, altura), Image.LANCZOS)
            logo_img_tk = ImageTk.PhotoImage(img)
            logo_label.config(image=logo_img_tk)
            logo_label.image = logo_img_tk

    logo_label = tk.Label(logo_container)
    logo_label.pack(expand=True)
    # Use debounce for resize event to avoid lag
    debounced_resize = Debounce(redimensionar_logo, wait=120)
    painel_esquerdo.bind("<Configure>", lambda e: debounced_resize())
    redimensionar_logo()
except Exception as e:
    logo_label = tk.Label(logo_container, text="[LOGO MONARCA]", fg="white", font=("Segoe UI", 18, "bold"))
    logo_label.pack(pady=5)

# --- Drag and Drop Fix ---
def drag_and_drop(event):
    arquivos = root.tk.splitlist(event.data)
    if arquivos:
        caminho = arquivos[0]
        if caminho.lower().endswith('.mc') and os.path.isfile(caminho):
            abrir_arquivo(caminho)
        else:
            messagebox.showerror("Erro", "Por favor, selecione um arquivo '.mc' válido.")

# Register drag and drop on root and painel_esquerdo for best coverage
for widget in (root, painel_esquerdo):
    widget.drop_target_register(DND_FILES)
    widget.dnd_bind('<<Drop>>', drag_and_drop)
    
# Checa se foi passado um .mc via linha de comando
if len(sys.argv) > 1:
    arquivo_cli = sys.argv[1]
    if os.path.isfile(arquivo_cli) and arquivo_cli.lower().endswith(".mc"):
        abrir_arquivo(arquivo_cli)
    else:
        messagebox.showerror("Erro", f"O arquivo passado não é válido: {arquivo_cli}")

aplicar_tema()
root.mainloop()