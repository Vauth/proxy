# - github.com/Vauth/proxy - #

import re
import requests
import threading

# Disable warnings for clean output
requests.packages.urllib3.disable_warnings()

# Retrieve bulk proxy list
class Providers:
    def __init__(self):
        self.all_proxies = []

    def Github(self):
        with open('resources/sources.txt', 'r') as file: proxylist = file.read().splitlines()
        for url in proxylist:
            try:
                response = requests.get(url, verify=False).text.splitlines()
                count = [self.all_proxies.append(i) for i in response]
                print("[+] Retrieved ({}) ({})".format(url.split('/')[3], len(count)))
            except Exception as e:
                print('[unexpected] {}'.format(e))
                pass

    def Retrieve(self):
        self.Github()
        return self.all_proxies

# Threading proxy checker
class ProxyChecker:
    def __init__(self, proxies):
        self.proxies = proxies
        self.valid_proxies = []
        self.lock = threading.Lock()

    def Check(self, proxy):
        try:
            testcase = 'http://connectivitycheck.gstatic.com/generate_204'
            response = requests.get(testcase, proxies={'http': proxy, 'https': proxy}, timeout=3, verify=False)
            if response.status_code == 204:
                with self.lock: self.valid_proxies.append(proxy)
                print("[+] {} UP".format(proxy))
                return True
            else:
                return False
        except requests.RequestException:
            return False

    def Run(self):
        threads = []
        for proxy in self.proxies:
            thread = threading.Thread(target=self.Check, args=(proxy,))
            threads.append(thread)
            thread.start()
        for thread in threads: thread.join()
        return self.valid_proxies

# Run the main program
proxies = (Providers()).Retrieve()
print('\n[info] Total Proxies: {}\n'.format(len(proxies)))
checker = (ProxyChecker(proxies)).Run()
print('\n[info] Alive Proxies: {}\n'.format(len(checker)))
with open('proxy.txt', 'w') as f: f.write('\n'.join(checker))
