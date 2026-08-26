# -*- coding: utf-8 -*-
# ilah.cc Kızlık Soyadı – Selenium + manuel chromedriver yolu (Termux uyumlu)
import sys
import time
import re
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

if len(sys.argv) < 2:
    sys.exit('Kullanım: python script.py TCKN')

TCKN = sys.argv[1].strip()
if not TCKN.isdigit() or len(TCKN) != 11:
    sys.exit('TCKN 11 haneli sayı olmalı.')

# === CHROMEDRIVER YOLU – TERMUX'TAKİ GERÇEK YOL ===
CHROME_DRIVER_PATH = "/data/data/com.termux/files/usr/bin/chromedriver"  # which chromedriver çıktısı

options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1920,1080')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

# === SERVICE İLE DRIVER'I BAŞLAT ===
service = Service(executable_path=CHROME_DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)
driver.set_page_load_timeout(30)

try:
    print("[*] Cloudflare challenge çözülüyor (30 saniye)...")
    driver.get('https://ilah.cc/')
    time.sleep(5)
    
    driver.get('https://ilah.cc/kızlık-soyadı-sorgu')
    time.sleep(3)
    
    # CSRF token (varsa)
    try:
        csrf = driver.find_element(By.NAME, '_token').get_attribute('value')
    except:
        csrf = ''
    
    # TC alanını bul ve doldur
    tc_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.NAME, 'tc_kimlik'))
    )
    tc_input.clear()
    tc_input.send_keys(TCKN)
    
    # Ara butonuna tıkla
    ara_buton = driver.find_element(By.XPATH, "//button[contains(text(),'Ara')] | //input[@value='Ara'] | //button[@type='submit']")
    ara_buton.click()
    time.sleep(3)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    metin = soup.get_text()
    
    eslesme = re.search(r'Kızlık\s*Soyadı\s*[:;]\s*([A-ZĞÜŞİÖÇI\s]+)', metin, re.IGNORECASE)
    if eslesme:
        print(f'Kızlık Soyadı: {eslesme.group(1).strip()}')
    else:
        yedek = re.search(r'>([A-ZĞÜŞİÖÇ]{3,})<', html)
        if yedek:
            print(f'Muhtemel kızlık soyadı: {yedek.group(1)}')
        else:
            print("Sonuç bulunamadı. Sayfa içeriği (ilk 1500 karakter):")
            print(metin[:1500])

except Exception as e:
    print(f"[!] Hata: {e}")
finally:
    driver.quit()