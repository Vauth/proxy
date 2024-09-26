# - github.com/Vauth/proxy - #

import re
import requests
import threading

# Retrieve bulk proxy list
class Providers:
    def __init__(self):
        self.all_proxies = []

    def NovaProxy(self):
        response = requests.get('https://api.proxynova.com/proxy/find?url=https://www.proxynova.com/proxy-server-list/country-cn/', verify=True)
        [self.all_proxies.append(f"{ii['ip']}:{ii['port']}") for ii in response.json()['proxies']]
        print("[+] Retrieved (NovaProxy)")

    def DitaProxy(self):
        response = requests.get(f'https://api.ditatompel.com/v1/proxy/country/cn?page=1&limit=100', verify=True)
        [self.all_proxies.append(i['type'].lower()+'://'+i['ip']+':'+str(i['port'])) for i in response.json()['data']['items']]
        print("[+] Retrieved (DitaProxy)")

    def ScrapeProxy(self):
        response = requests.get('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=cn&proxy_format=protocolipport&format=json', verify=True)
        [self.all_proxies.append(i['protocol'].lower()+'://'+i['ip']+':'+str(i['port'])) for i in response.json()['proxies']]
        print("[+] Retrieved (ScrapeProxy)")

    def EliteProxy(self):
        nonce = re.search(r'"nonce":"(.*?)"', requests.get('https://proxyelite.info/free-proxy-list/', verify=True).text).group(1)
        filters = {"country": "China", "latency": 0, "page_size": 100, "page": 1}
        response = requests.get(f'https://proxyelite.info/wp-admin/admin-ajax.php?action=proxylister_download&nonce={nonce}&format=txt&filter={filters}', verify=True).text.splitlines()
        [self.all_proxies.append('http://'+i) for i in response]
        print("[+] Retrieved (EliteProxy)")

    def FreeonlyProxy(self):
        response = requests.get('https://proxyfreeonly.com/api/free-proxy-list?limit=500&page=1&country=CN&sortBy=lastChecked&sortType=desc', verify=True)
        [self.all_proxies.append(i['protocols'][0].lower() + '://' + i['ip'] + ':' + str(i['port'])) for i in response.json()]
        print("[+] Retrieved (Freeonly)")

    def PdbProxy(self):
        response = requests.post('https://proxydb.net/list', data={'country': 'CN'}, verify=True)
        [self.all_proxies.append(i['type'].lower() + '://' + i['ip'] + ':' + str(i['port'])) for i in response.json()['proxies']]
        print("[+] Retrieved (Pdb)")

    def Retrieve(self):
        try:
            self.NovaProxy()
            self.DitaProxy()
            self.EliteProxy()
            self.ScrapeProxy()
            self.FreeonlyProxy()
            self.PdbProxy()
        except:
            pass

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
            response = requests.get(testcase, proxies={'http': proxy, 'https': proxy}, timeout=3)
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
print('\n[info] Total proxies: {}\n'.format(len(proxies)))
checker = (ProxyChecker(proxies)).Run()
with open('proxy.txt', 'w') as f: f.write('\n'.join(checker))
