import os
import time

import httpx
import threading
from itertools import cycle
import colorama
import concurrent.futures

i = 0

colorama.init(convert=True)

proxy_iter = cycle(open("proxies.txt").read().splitlines())


def has_billing(token: str) -> bool:
    while True:
        proxy = next(proxy_iter)
        proxies = {
            "https://": f"http://{proxy}",
        }
        client = httpx.Client(proxies=proxies)
        resp = client.get(
            url="https://discord.com/api/v9/users/@me/billing/payment-sources",
            headers={
                "authorization": token,
                "x-super-properties": "eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MDA2Iiwib3NfdmVyc2lvbiI6IjEwLjAuMjIwMDAiLCJvc19hcmNoIjoieDY0Iiwic3lzdGVtX2xvY2FsZSI6ImVuLVVTIiwiY2xpZW50X2J1aWxkX251bWJlciI6MTQ0MDU3LCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9006 Chrome/91.0.4472.164 Electron/13.6.6 Safari/537.36"
            },
            timeout=5
        )
        if resp.status_code == 200:
            for source in resp.json() and len(resp.json()):
                if source["invalid"]:
                    return False
            return True
        return False


def check_token(token: str) -> None:
    global i
    i += 1
    check = has_billing(token)
    if check:
        with open("tokens/billing.txt", "a") as f:
            f.write(f"{token}\n")
        print(f"[{i}] {colorama.Fore.GREEN}{token[0:-54]} has billing")
    else:
        with open("tokens/non-billing.txt", "a") as f:
            f.write(f"{token}\n")
        print(f"[{i}] {colorama.Fore.RED}{token[0:-54]} does not have billing")


tokens = []
with open("tokens.txt", "r") as f:
    for line in f:
        tokens.append(line.strip())

if not os.path.exists("tokens"):
    os.mkdir("tokens")

with open("tokens/billing.txt", "w") as f:
    f.write("")
with open("tokens/non-billing.txt", "w") as f:
    f.write("")


with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for token in tokens:
        futures.append(executor.submit(check_token, token=token))
    for future in concurrent.futures.as_completed(futures):
        print(future.result())
