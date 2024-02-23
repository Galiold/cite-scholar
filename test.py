import requests

socks_proxies = dict(http='socks5://0.0.0.0:9999', https='socks5://0.0.0.0:9999')

def get(url):
    return requests.get(url=url)

def get_with_proxy(url):
    return requests.get(url=url, proxies=socks_proxies)


print(get_with_proxy('https://ipinfo.io').text)