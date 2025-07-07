import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, ImageSequence
import os
import subprocess
import sys
import threading
import webbrowser
import json
import random
# Inicialização do Pygame para áudio
try:
    import pygame
    pygame.mixer.init()
    PYGAME_DISPONIVEL = True
except (ImportError, Exception) as e:
    PYGAME_DISPONIVEL = False

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
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

if not os.path.exists(ASSETS_DIR):
    os.makedirs(ASSETS_DIR)

processo = None
comando_historico = []
historico_index = 0

# Usamos TkinterDnD.Tk ao invés de tk.Tk para suportar drag and drop
root = TkinterDnD.Tk()
root.title("Launcher Monarca")
root.geometry("1235x600")
root.minsize(800, 500)

style = ttk.Style(root)
style.theme_use('clam')
def ppt(escolha):
    numpc = random.randint(1,3)
    numu = 1 if escolha == "pedra" else 2 if escolha == "papel" else 3
    terminal_output.insert("end", f"O computador escolheu {'pedra' if numpc == 1 else 'papel' if numpc == 2 else 'tesoura'} \n")
    if numpc == numu:
        terminal_output.insert("end", "Empate!\n")
    elif (numu == 1 and numpc == 3) or (numu == 2 and numpc == 1) or (numu == 3 and numpc == 2):
        terminal_output.insert("end", "Você venceu!\n")
    else:
        terminal_output.insert("end", "Você perdeu!\n")

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
    logo_subtext_label.config(bg=tema_cores["left_panel_bg"], fg=tema_cores["button_fg"])

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

def navegar_historico_cima(event):
    global historico_index
    if comando_historico and historico_index > 0:
        historico_index -= 1
        input_entry.delete(0, tk.END)
        input_entry.insert(0, comando_historico[historico_index])
        return "break"

def navegar_historico_baixo(event):
    global historico_index
    if comando_historico and historico_index < len(comando_historico) - 1:
        historico_index += 1
        input_entry.delete(0, tk.END)
        input_entry.insert(0, comando_historico[historico_index])
    elif historico_index == len(comando_historico) - 1:
        historico_index += 1
        input_entry.delete(0, tk.END)
    return "break"

def enviar_input(event=None):
    global historico_index
    texto_original = input_entry.get()
    if not texto_original:
        return

    if not comando_historico or comando_historico[-1] != texto_original:
        comando_historico.append(texto_original)
    historico_index = len(comando_historico)

    texto_comando = texto_original.lower().strip()
    input_entry.delete(0, tk.END)

    # Se um script estiver em execução, envia o input para ele
    if processo and processo.poll() is None:
        try:
            terminal_output.insert("end", texto_original + "\n")
            terminal_output.see("end")
            if processo.stdin:
                processo.stdin.write(texto_original + "\n")
                processo.stdin.flush()
        except (IOError, BrokenPipeError):
            terminal_output.insert("end", "\n[Processo encerrado, não é possível enviar input.]\n")
            terminal_output.see("end")
        except Exception as e:
            print("Erro ao enviar input:", e)
    else:
        # Se nenhum script estiver rodando, processa comandos locais/easter eggs
        terminal_output.insert("end", f"> {texto_original}\n") # Echo do comando
        input_easteregg = texto_comando.lower()
        if input_easteregg == "tutorial":
            mostrar_tutorial()
        elif input_easteregg == "arthur morgan":
            terminal_output.insert("end", "He was a good man...\n")
        elif input_easteregg == "iddqd":
            terminal_output.insert("end", "God mode ativado.\n")
        elif input_easteregg == "up up down down left right left right b a":
            terminal_output.insert("end", "Konami Code detectado. Modo debug ativo.\n")
        elif input_easteregg == "bolo" or input_easteregg == "cake":
            terminal_output.insert("end", "The cake is a lie.\n")
        elif input_easteregg == "fus ro dah":
            terminal_output.insert("end", "Você gritou tão forte que apagou o interpretador.\n")
        elif input_easteregg == "i need healing":
            terminal_output.insert("end", "Você digitou isso 12 vezes nos últimos 2 minutos. Genji detectado.\n")
        elif input_easteregg == "minecraft":
            terminal_output.insert("end", "The end?\n")
        elif input_easteregg == "sus":
            terminal_output.insert("end", "amogus\n")
            play_easter_egg("sus")
        elif input_easteregg == "nmap -ss 127.0.0.1":
            terminal_output.insert("end", "Aqui não.\n")
        elif input_easteregg == "sudo rm -rf":
            terminal_output.insert("end", "Não vai rolar.\n")
        elif input_easteregg == "telnet towel.blinkenlights.nl":
            terminal_output.insert("end", "Isso não funciona aqui, mas parabéns por tentar...\n")
        elif input_easteregg == "hello world":
            terminal_output.insert("end", "Você é oficialmente um programador júnior agora.\n")
        elif input_easteregg == "roll d20":
            play_easter_egg("d20")
            r = random.randint(1, 20)
            if r == 1:
                terminal_output.insert("end", "Você tropeça e bate a cabeça no chão.\n")
            elif r == 20:
                terminal_output.insert("end", "Acerto crítico: você compila de primeira.\n")
            else:
                terminal_output.insert("end", f"Você rolou {r}. Nada épico, nada vergonhoso.\n")
        elif input_easteregg == "cast fireball":
            terminal_output.insert("end", "🧙 Você causou 8d6 de dano. O terminal agora está levemente chamuscado.\n")
        elif input_easteregg == "whoami":
            terminal_output.insert("end", "Você é quem digita. Mas será que você é quem decide?\n")
        elif input_easteregg == "help me":
            terminal_output.insert("end", "VOCÊ NÃO PRECISA DE AJUDA, VOCÊ PRECISA DE CORAGEM\n")
        elif input_easteregg == "rickroll":
            play_easter_egg("rickroll")
        elif input_easteregg == "start game":
            terminal_output.insert("end", "Você acorda em um terminal escuro. Uma opção pisca: 'iniciar'\n")
        elif input_easteregg == "hogwarts":
            terminal_output.insert("end", "Diretamente de Hogwarts, Wingardium Levirola\n")
            play_easter_egg("hogwarts")
        elif input_easteregg == "this is what you asked for":
            play_easter_egg("linkinpark")
            terminal_output.insert("end", "Heavy is the crown\nFire in the sunrise, ashes raining down\nTrying to hold it in\nBut it keeps bleeding out\nThis is what you asked for, heavy is the\nHeavy is the crown!\n")
        elif input_easteregg == "cyberpunk":
            play_easter_egg("cyberpunk")
            terminal_output.insert("end", "Wake the fuck up, Samurai.\nWe got a city to burn.\n")
        elif input_easteregg == "make me a sandwich":
            terminal_output.insert("end", "What? Make it yourself.\n")
        elif input_easteregg == "sudo make me a sandwich":
            terminal_output.insert("end", "Okay.")
        elif input_easteregg == "42":
            terminal_output.insert("end", "Resposta para a Vida, o Universo e Tudo Mais.\n")
        elif input_easteregg == "big smoke":
            play_easter_egg("smoke")
            terminal_output.insert("end", "I'll have two number 9's, a number 9 large,\na number 6 with extra dip, a number 7,\ntwo number 45's, one with cheese, and a large soda.\n")
        elif input_easteregg == "hesoyam":
            play_easter_egg("gta")
            terminal_output.insert("end", "Trapaça ativada.\n")
        elif input_easteregg == "shrek is love":
            terminal_output.insert("end", "Shrek é vida.\n")
        elif input_easteregg == "cavalo":
            play_easter_egg("vacalo")
        elif input_easteregg == "interagir" or input_easteregg == "z" or input_easteregg == "undertale":
            terminal_output.insert("end", "Interagir com o terminal te enche de determinação.\n")
            play_easter_egg("undertale")
        elif input_easteregg == "draven":
            num = random.randint(1, 2)
            if num == 1:
                terminal_output.insert("end", "Bem vindos a League of Draven!\n")
                play_easter_egg("leaguedraven")
            else:
                terminal_output.insert("end", "Não é Dráven. É Draaaaven.\n")
                play_easter_egg("draven")
        elif input_easteregg == "akali":
            terminal_output.insert("end", "Temam a assassina sem mestre.\n")
            play_easter_egg("akali")
        elif input_easteregg == "zomboid" or input_easteregg == "project zomboid":
            terminal_output.insert("end", "This is how you died.\n")
            play_easter_egg("zomboid")
        elif input_easteregg == "pedra":
            ppt('pedra')
        elif input_easteregg == "papel":
            ppt('papel')
        elif input_easteregg == "tesoura":
            ppt('tesoura')
        elif input_easteregg in ["limpar", "clr", "clear"]:
            terminal_output.delete("1.0", "end")
        elif input_easteregg == "ajuda" or input_easteregg == "help" or input_easteregg == "comandos":
            terminal_output.insert("end", "Comandos disponíveis:\n")
            terminal_output.insert("end", "- tutorial: Inicia o tutorial interativo.\n")
            terminal_output.insert("end", "- limpar/clr/clear: Limpa o terminal.\n")
            terminal_output.insert("end", "- docs: Abre a documentação do Monarca.\n")
            terminal_output.insert("end", "- *frase secreta*: lista todos os easter eggs, apenas os alunos mais perspicazes de Koiller\nsaberão qual frase é.\n")
        elif input_easteregg == "docs":
            abrir_documentacao()
        elif input_easteregg == "totó é um mamífero":
            terminal_output.insert("end", "lista de easter eggs:\n")
            terminal_output.insert("end", "1 - arthur morgan\n")
            terminal_output.insert("end", "2 - iddqd\n")
            terminal_output.insert("end", "3 - up up down down left right left right b a\n")
            terminal_output.insert("end", "4 - bolo/cake\n")
            terminal_output.insert("end", "5 - fus ro dah\n")
            terminal_output.insert("end", "6 - i need healing\n")
            terminal_output.insert("end", "7 - minecraft\n")
            terminal_output.insert("end", "8 - sus\n")
            terminal_output.insert("end", "9 - nmap -sS 127.0.0.1\n")
            terminal_output.insert("end", "10 - sudo rm -rf\n")
            terminal_output.insert("end", "11 - telnet towel.blinkenlights.nl\n")
            terminal_output.insert("end", "12 - hello world\n")
            terminal_output.insert("end", "13 - roll d20\n")
            terminal_output.insert("end", "14 - cast fireball\n")
            terminal_output.insert("end", "15 - whoami\n")
            terminal_output.insert("end", "16 - help me\n")
            terminal_output.insert("end", "17 - rickroll\n")
            terminal_output.insert("end", "18 - start game\n")
            terminal_output.insert("end", "19 - hogwarts\n")
            terminal_output.insert("end", "20 - this is what you asked for\n")
            terminal_output.insert("end", "21 - cyberpunk\n")
            terminal_output.insert("end", "22 - make me a sandwich\n")
            terminal_output.insert("end", "23 - sudo make me a sandwich\n")
            terminal_output.insert("end", "24 - 42\n")
            terminal_output.insert("end", "25 - big smoke\n")
            terminal_output.insert("end", "26 - hesoyam\n")
            terminal_output.insert("end", "27 - shrek is love\n")
            terminal_output.insert("end", "28 - cavalo\n")
            terminal_output.insert("end", "29 - interagir/z/undertale\n")
            terminal_output.insert("end", "30 - draven\n")
            terminal_output.insert("end", "31 - akali\n")
            terminal_output.insert("end", "32 - zomboid/project zomboid\n")
            terminal_output.insert("end", "33 - pedra/papel/tesoura\n")
        else:
            terminal_output.insert("end", f"Comando '{texto_comando}' não reconhecido. Selecione um script para executar ou use 'tutorial'.\n")
        terminal_output.see("end")

input_entry.bind("<Return>", enviar_input)
input_entry.bind("<Up>", navegar_historico_cima)
input_entry.bind("<Down>", navegar_historico_baixo)

def animate_gif(window, label, frames, frame_index=0):
    """Função recursiva para animar um GIF em um widget Label."""
    try:
        frame = frames[frame_index]
        label.config(image=frame)
        frame_index = (frame_index + 1) % len(frames)
        # A velocidade da animação pode ser ajustada (aqui, 100ms por frame)
        window.after(100, animate_gif, window, label, frames, frame_index)
    except tk.TclError:
        # A janela foi fechada, para a animação
        pass

def play_easter_egg(name):
    """
    Procura e reproduz um arquivo de mídia (áudio/imagem/gif) para um easter egg.
    A busca é feita na pasta 'assets'.
    """
    audio_exts = ['.mp3', '.wav']
    image_exts = ['.gif', '.png', '.jpg', '.jpeg']

    # Procura por áudio primeiro
    if PYGAME_DISPONIVEL:
        for ext in audio_exts:
            path = os.path.join(ASSETS_DIR, f"{name}{ext}")
            if os.path.exists(path):
                try:
                    # Toca o som em uma thread separada para não bloquear a UI
                    def play_sound():
                        pygame.mixer.music.load(path)
                        pygame.mixer.music.play()
                    threading.Thread(target=play_sound, daemon=True).start()
                    return # Para aqui se encontrar um áudio
                except Exception as e:
                    print(f"Erro ao tocar áudio {path}: {e}")

    # Se não encontrou áudio, procura por imagem/gif
    for ext in image_exts:
        path = os.path.join(ASSETS_DIR, f"{name}{ext}")
        if os.path.exists(path):
            try:
                win = tk.Toplevel(root)
                win.title(name.replace("_", " ").title())
                win.resizable(False, False)

                img_raw = Image.open(path)

                # --- Lógica de redimensionamento ---
                largura_painel = painel_esquerdo.winfo_width()
                largura_alvo = int(largura_painel * 0.8)
                
                proporcao = img_raw.height / img_raw.width
                altura_alvo = int(largura_alvo * proporcao)
                # --- Fim da lógica de redimensionamento ---

                if ext == '.gif':
                    # Redimensiona cada frame do GIF
                    frames_resized = []
                    for frame in ImageSequence.Iterator(img_raw):
                        frame_resized = frame.copy().resize((largura_alvo, altura_alvo), Image.LANCZOS)
                        frames_resized.append(ImageTk.PhotoImage(frame_resized))
                    
                    label = tk.Label(win, borderwidth=0)
                    label.pack()
                    win.after(0, animate_gif, win, label, frames_resized)
                else:
                    img_resized = img_raw.resize((largura_alvo, altura_alvo), Image.LANCZOS)
                    img_tk = ImageTk.PhotoImage(img_resized)
                    label = tk.Label(win, image=img_tk, borderwidth=0)
                    label.image = img_tk  # Mantém referência para evitar garbage collection
                    label.pack()

                # Centraliza a janela pop-up na janela principal
                win.transient(root) # Associa a janela pop-up à principal
                win.update_idletasks()

                # Calcula a posição para centralizar a janela pop-up em relação à janela principal
                root_x = root.winfo_x()
                root_y = root.winfo_y()
                root_width = root.winfo_width()
                root_height = root.winfo_height()

                win_width = win.winfo_width()
                win_height = win.winfo_height()

                pos_x = root_x + (root_width // 2) - (win_width // 2)
                pos_y = root_y + (root_height // 2) - (win_height // 2)

                win.geometry(f"+{pos_x}+{pos_y}")
                return # Para aqui se encontrar uma imagem
            except Exception as e:
                print(f"Erro ao exibir imagem {path}: {e}")

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
    # State machine to strip ANSI escape codes while reading char by char
    # This avoids buffering issues with interactive input prompts
    state = "NORMAL"  # Can be "NORMAL", "GOT_ESC", "IN_SEQ"
    while True:
        char = stream.read(1)
        if char == "" and processo.poll() is not None:
            break
        if not char:
            continue

        if state == "NORMAL":
            if char == '\033':
                state = "GOT_ESC"
            else:
                terminal_output.insert("end", char)
                terminal_output.see("end")
        elif state == "GOT_ESC":
            if char == '[':
                state = "IN_SEQ"
            else:
                state = "NORMAL" # Not a CSI sequence, consume and reset
        elif state == "IN_SEQ":
            if '@' <= char <= '~':  # Sequence ends with a char in this range
                state = "NORMAL"
            # else: still in sequence, so we consume the char by doing nothing

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
    webbrowser.open_new_tab("https://github.com/Monarca-lang/Monarca/blob/main/documentacao.md")

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
versao_interpretador = "Versão do interpretador: bom o suficiente (turing-complete)" #+ sys.version.split()[0]
versao_launcher = "Versão do Launcher: 4.2.0"  # Pode pegar dinamicamente se tiver como

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

# Texto embaixo do logo
logo_subtext_label = tk.Label(logo_container, text='"Eu sou mais louco que todos vocês."', font=("Segoe UI", 8, "italic"), fg="#696969")
logo_subtext_label.pack(side="bottom", pady=(0, 10))

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
        altura = int(painel_esquerdo.winfo_height() * 0.35)
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
    logo_label = tk.Label(logo_container, text="[logo aqui]", fg="white", font=("Segoe UI", 18, "bold"))
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