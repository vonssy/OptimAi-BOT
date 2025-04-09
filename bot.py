from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from fake_useragent import FakeUserAgent
from datetime import datetime
from colorama import *
import asyncio, base64, json, os, pytz

wib = pytz.timezone('Asia/Jakarta')

class Optimai:
    def __init__(self) -> None:
        self.headers = {
            "Accept": "*/*",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Origin": "chrome-extension://njlfcjdojmopagogfpjgcbnpmiknapnd",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Storage-Access": "active",
            "User-Agent": FakeUserAgent().random
        }
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(
            f"""
        {Fore.GREEN + Style.BRIGHT}Auto Ping {Fore.BLUE + Style.BRIGHT}Optimai - BOT
            """
            f"""
        {Fore.GREEN + Style.BRIGHT}Rey? {Fore.YELLOW + Style.BRIGHT}<INI WATERMARK>
            """
        )

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
    
    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}File {filename} Not Found.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []
    
    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/all.txt") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = content.splitlines()
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}File {filename} Not Found.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = f.read().splitlines()
            
            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}No Proxies Found.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Proxies Total  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )
        
        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Failed To Load Proxies: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, email):
        if email not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[email] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[email]

    def rotate_proxy_for_account(self, email):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[email] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy
    
    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"
        
        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account

    def decode_response_data(self, data):
        decoded = base64.b64decode(data).decode('utf-8')
        filtered = ''.join([char for i, char in enumerate(decoded) if (i + 1) % 5 != 0])
        reversed_str = filtered[::-1]
        a = 7
        
        result = ''.join(
            chr(int(reversed_str[i:i+2], 16) ^ (a + i//2))
            for i in range(0, len(reversed_str), 2)
        )
        return result

    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Account:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Status:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print("1. Run With Monosans Proxy")
                print("2. Run With Private Proxy")
                print("3. Run Without Proxy")
                choose = int(input("Choose [1/2/3] -> ").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "Run With Monosans Proxy" if choose == 1 else 
                        "Run With Private Proxy" if choose == 2 else 
                        "Run Without Proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}{proxy_type} Selected.{Style.RESET_ALL}")
                    return choose
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Please enter either 1, 2 or 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Invalid input. Enter a number (1, 2 or 3).{Style.RESET_ALL}")
    
    async def register_nodes(self, access_token: str, register_payload: str, proxy=None, retries=5):
        url = "https://api.optimai.network/devices/register-v2"
        data = json.dumps({"data":register_payload})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(access_token, proxy, Fore.RED, f"Registering Nodes Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
    
    async def update_uptime(self, access_token: str, uptime_payload: str, proxy=None, retries=5):
        url = "https://api.optimai.network/uptime/online"
        data = json.dumps({"data":uptime_payload})
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
            "Content-Length": str(len(data)),
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, data=data) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(access_token, proxy, Fore.RED, f"Update Uptime Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
    
    async def perform_checkin(self, access_token: str, proxy=None, retries=5):
        url = "https://api.optimai.network/daily-tasks/check-in"
        headers = {
            **self.headers,
            "Authorization": f"Bearer {access_token}",
            "Content-Length": "2",
            "Content-Type": "application/json"
        }
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=120)) as session:
                    async with session.post(url=url, headers=headers, json={}) as response:
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                return self.print_message(access_token, proxy, Fore.RED, f"Perform Chechk-In Failed: {Fore.YELLOW + Style.BRIGHT}{str(e)}")
            
    async def process_register_nodes(self, access_token: str, register_payload: str, uptime_payload: str, use_proxy: bool):
        proxy = self.get_next_proxy_for_account(access_token) if use_proxy else None
        nodes = None
        while nodes is None:
            nodes = await self.register_nodes(access_token, register_payload, proxy)
            if not nodes:
                proxy = self.rotate_proxy_for_account(access_token) if use_proxy else None
                await asyncio.sleep(5)
                continue

            register_response = nodes.get("data", {})
            register_result = json.loads(self.decode_response_data(register_response))
            if register_result and register_result.get("device_id"):
                self.print_message(access_token, proxy, Fore.GREEN, "Registering Nodes Success")
                
                await self.process_update_uptime(access_token, uptime_payload, use_proxy)

            nodes = None
            self.print_message(access_token, proxy, Fore.RED, "Registering Nodes Failed")
            await asyncio.sleep(5)
            continue

    async def process_update_uptime(self, access_token: str, uptime_payload: str, use_proxy: bool):
        while True:
            await asyncio.sleep(10 * 60)

            proxy = self.get_next_proxy_for_account(access_token) if use_proxy else None
            updated = await self.update_uptime(access_token, uptime_payload, proxy)
            if updated:
                updated_response = updated.get("data", {})
                updated_result = json.loads(self.decode_response_data(updated_response))
                if updated_result and updated_result.get("reward"):
                    reward = updated_result.get("reward", 0)
                    self.print_message(access_token, proxy, Fore.GREEN, 
                        "Uptime Updated Successfully "
                        f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                        f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                        f"{Fore.WHITE + Style.BRIGHT}+{reward} OPI{Style.RESET_ALL}"
                    )
                else:
                    self.print_message(access_token, proxy, Fore.RED, "Update Uptime Failed")
            
    async def process_perform_checkin(self, access_token: str, use_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(access_token) if use_proxy else None
            claim = await self.perform_checkin(access_token, proxy)
            if claim and claim.get("message") == "Check-in successful":
                reward = claim.get("reward")
                self.print_message(access_token, proxy, Fore.GREEN, 
                    "Check-In Success "
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Reward: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}+{reward} OPI{Style.RESET_ALL}"
                )
            elif claim and claim.get("message") == "Check-in already completed for today":
                self.print_message(access_token, proxy, Fore.YELLOW, "Already Check-In Today")
            
            await asyncio.sleep(12 * 60 * 60)
        
    async def process_accounts(self, access_token: str, register_payload: str, uptime_payload: str, use_proxy: bool):
        tasks = []
        tasks.append(asyncio.create_task(self.process_perform_checkin(access_token, use_proxy)))
        tasks.append(asyncio.create_task(self.process_register_nodes(access_token, register_payload, uptime_payload, use_proxy)))
        await asyncio.gather(*tasks)
        
    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED + Style.BRIGHT}No Accounts Loaded.{Style.RESET_ALL}")
                return
            
            use_proxy_choice = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Account's Total: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}-{Style.RESET_ALL}"*75)

            while True:
                tasks = []
                for account in accounts:
                    if account:
                        access_token = account["accessToken"]
                        register_payload = account["registerPayload"]
                        uptime_payload = account["uptimePayload"]

                        if access_token and register_payload and uptime_payload:
                            tasks.append(asyncio.create_task(self.process_accounts(access_token, register_payload, uptime_payload, use_proxy)))

                await asyncio.gather(*tasks)
                await asyncio.sleep(10)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Error: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Optimai()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ EXIT ] Optimai - BOT{Style.RESET_ALL}                                       "                              
        )