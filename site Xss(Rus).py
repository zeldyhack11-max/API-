from colorama import init, Fore, Back, Style
init()
import random
import requests
from bs4 import BeautifulSoup
import re



red = Fore.RED
cyan = Fore.CYAN
blue = Fore.BLUE
green = Fore.GREEN

yellow = Fore.YELLOW
reset = Style.RESET_ALL
bold = Style.BRIGHT

versions = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{0}.0) Gecko/{0}{1:02d} Firefox/{0}.0",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:{0}.0) Gecko/{0}{1:02d} Firefox/{0}.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.{0}; rv:{1}.0) Gecko/20{2:02d}{3:02d} Firefox/{1}.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:{0}.0) Gecko/{0}{1:02d} Firefox/{0}.0",
]

random_version = random.choice(versions).format(random.randint(10, 99), random.randint(0, 9), random.randint(0, 99), random.randint(0, 99))
headers = {"User-Agent": random_version}

banner_list = [
	"""
███████╗███████╗███╗   ██╗██╗████████╗██╗  ██╗     ████████╗██████╗  █████╗  ██████╗██╗  ██╗███████╗██████╗ 
╚══███╔╝██╔════╝████╗  ██║██║╚══██╔══╝██║  ██║     ╚══██╔══╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
  ███╔╝ █████╗  ██╔██╗ ██║██║   ██║   ███████║        ██║   ██████╔╝███████║██║     █████╔╝ █████╗  ██████╔╝
 ███╔╝  ██╔══╝  ██║╚██╗██║██║   ██║   ██╔══██║        ██║   ██╔══██╗██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
███████╗███████╗██║ ╚████║██║   ██║   ██║  ██║███████╗██║   ██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚══════╝╚══════╝╚═╝  ╚═══╝╚═╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
	""",
	"""
    )          )  (               )            (                         )       (    
 ( /(       ( /(  )\ )  *   )  ( /(      *   ) )\ )    (        (     ( /(       )\ ) 
 )\()) (    )\())(()/(` )  /(  )\())   ` )  /((()/(    )\       )\    )\()) (   (()/( 
((_)\  )\  ((_)\  /(_))( )(_))((_)\     ( )(_))/(_))((((_)(   (((_) |((_)\  )\   /(_))
 _((_)((_)  _((_)(_)) (_(_())  _((_)   (_(_())(_))   )\ _ )\  )\___ |_ ((_)((_) (_))  
|_  / | __|| \| ||_ _||_   _| | || |   |_   _|| _ \  (_)_\(_)((/ __|| |/ / | __|| _ \ 
 / /  | _| | .` | | |   | |   | __ |     | |  |   /   / _ \   | (__   ' <  | _| |   / 
/___| |___||_|\_||___|  |_|   |_||_|_____|_|  |_|_\  /_/ \_\   \___| _|\_\ |___||_|_\ 
                                   |_____|                                            
	""",
	"""
 ███████████ ██████████ ██████   █████ █████ ███████████ █████   █████           ███████████ ███████████     █████████     █████████  █████   ████ ██████████ ███████████  
░█░░░░░░███ ░░███░░░░░█░░██████ ░░███ ░░███ ░█░░░███░░░█░░███   ░░███           ░█░░░███░░░█░░███░░░░░███   ███░░░░░███   ███░░░░░███░░███   ███░ ░░███░░░░░█░░███░░░░░███ 
░     ███░   ░███  █ ░  ░███░███ ░███  ░███ ░   ░███  ░  ░███    ░███           ░   ░███  ░  ░███    ░███  ░███    ░███  ███     ░░░  ░███  ███    ░███  █ ░  ░███    ░███ 
     ███     ░██████    ░███░░███░███  ░███     ░███     ░███████████               ░███     ░██████████   ░███████████ ░███          ░███████     ░██████    ░██████████  
    ███      ░███░░█    ░███ ░░██████  ░███     ░███     ░███░░░░░███               ░███     ░███░░░░░███  ░███░░░░░███ ░███          ░███░░███    ░███░░█    ░███░░░░░███ 
  ████     █ ░███ ░   █ ░███  ░░█████  ░███     ░███     ░███    ░███               ░███     ░███    ░███  ░███    ░███ ░░███     ███ ░███ ░░███   ░███ ░   █ ░███    ░███ 
 ███████████ ██████████ █████  ░░█████ █████    █████    █████   █████ █████████    █████    █████   █████ █████   █████ ░░█████████  █████ ░░████ ██████████ █████   █████
░░░░░░░░░░░ ░░░░░░░░░░ ░░░░░    ░░░░░ ░░░░░    ░░░░░    ░░░░░   ░░░░░ ░░░░░░░░░    ░░░░░    ░░░░░   ░░░░░ ░░░░░   ░░░░░   ░░░░░░░░░  ░░░░░   ░░░░ ░░░░░░░░░░ ░░░░░   ░░░░░ 
	"""
]


banner_2 = """

**************************
*======@Zenith_link======*
 Crack by: @RigOlit      
 Support crack: @loggerspy
**************************

[1]Xss сканер          [3]Xss иньекция

[2]Ip логер (in dev)   [5]Выйти из тула

"""



banner = random.choice(banner_list)

print(f"{cyan}{banner}")

print(f"{red}{banner_2}")

choice = input(f"Выберите номер: ")

if choice == "1":
  xss_scan_url = input(f"{red}Ссылка на сайт: ")
  response = requests.get(xss_scan_url)
  soup = BeautifulSoup(response.text, "html.parser")
  forms = soup.find_all("form")
  for form in forms:
    action = form.get("action")
    method = form.get("method")
    print(f"Form Action: {action}")
    print( f"Method: {method}")
    inputs = form.find_all("input")
    for input in inputs:
      input_name = input.get("name")
      print(f"Найден инпут с название: {input_name}")

elif choice == "2":
  print("Времено не доступно")


elif choice == "3":
  xss_scan_url = input(f"{red}Ссылка на сайт: ")
  xss_Injection = input(f"{green}Ваша инъекция: ")

  response = requests.get(xss_scan_url, headers=headers)
  soup = BeautifulSoup(response.text, "html.parser")

  forms = soup.find_all("form")

  for form in forms:
      action = form.get("action")
      method = form.get("method", "get").lower()
      form_url = xss_scan_url if action.startswith('#') else action

      if not form_url.startswith("http"):
          from urllib.parse import urljoin
          form_url = urljoin(xss_scan_url, form_url)

      print(f"Form Action: {action}")
      print(f"Method: {method}")

      inputs = form.find_all("input")
      form_data = {}
      for input in inputs:
          input_name = input.get("name")
          input_type = input.get("type", "text")
          if input_name:
              form_data[input_name] = xss_Injection if input_type != "submit" else input.get("value")

      if method == "post":
          reque = requests.post(form_url, data=form_data, headers=headers)
      else:
          reque = requests.get(form_url, params=form_data, headers=headers)

      if reque.status_code == 200:
          print(f"{cyan}XSS запрос удачно отправлен в {form_url}")
elif choice == "4":
  sys.exit()
