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

    def DitaProxy(self):
        response = requests.get(f'https://api.ditatompel.com/v1/proxy/country/cn?page=1&limit=100', verify=False)
        count = [self.all_proxies.append(i['type'].lower()+'://'+i['ip']+':'+str(i['port'])) for i in response.json()['data']['items']]
        print("[+] Retrieved (DitaProxy) ({})".format(len(count)))

    def ScrapeProxy(self):
        response = requests.get('https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&country=cn&proxy_format=protocolipport&format=json', verify=False)
        count = [self.all_proxies.append(i['protocol'].lower()+'://'+i['ip']+':'+str(i['port'])) for i in response.json()['proxies']]
        print("[+] Retrieved (ScrapeProxy) ({})".format(len(count)))

    def EliteProxy(self):
        nonce = re.search(r'"nonce":"(.*?)"', requests.get('https://proxyelite.info/free-proxy-list/', verify=False).text).group(1)
        filters = {"country": "China", "latency": 0, "page_size": 100, "page": 1}
        response = requests.get(f'https://proxyelite.info/wp-admin/admin-ajax.php?action=proxylister_download&nonce={nonce}&format=txt&filter={filters}', verify=False).text.splitlines()
        count = [self.all_proxies.append('http://'+i) for i in response]
        print("[+] Retrieved (EliteProxy) ({})".format(len(count)))

    def PdbProxy(self):
        response = requests.post('https://proxydb.net/list', data={'country': 'CN'}, verify=False)
        count = [self.all_proxies.append(i['type'].lower() + '://' + i['ip'] + ':' + str(i['port'])) for i in response.json()['proxies']]
        print("[+] Retrieved (PdbProxy) ({})".format(len(count)))

    def GeonodeProxy(self):
        response = requests.get('https://proxylist.geonode.com/api/proxy-list?country=CN&limit=500&page=1&sort_by=lastChecked&sort_type=desc', verify=False)
        count = [self.all_proxies.append(i['protocols'][0].lower() + '://' + i['ip'] + ':' + str(i['port'])) for i in response.json()['data']]
        print("[+] Retrieved (GeonodeProxy) ({})".format(len(count)))

    def Retrieve(self):
        try:
            self.DitaProxy()
            self.EliteProxy()
            self.ScrapeProxy()
            self.PdbProxy()
            self.GeonodeProxy()
        except Exception as e:
            print('\n[unexpected] {}\n'.format(e))
            continue

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
print('\n[report] Alive Proxies: {}\n'.format(len(checker)))
with open('proxy.txt', 'w') as f: f.write('\n'.join(checker))
