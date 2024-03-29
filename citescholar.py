from bs4 import BeautifulSoup
import pyperclip as pc
import bibtexparser
import requests
import random
import time
import datetime
import argparse
import browser_cookie3
from tqdm import tqdm
import os

class API:
    def __init__(self, proxy_port=None) -> None:
        self.cookies = browser_cookie3.chrome(domain_name='.google.com')

        if proxy_port is not None:
            self.proxies = dict(http=f'socks5://0.0.0.0:{proxy_port}',
                                https=f'socks5://0.0.0.0:{proxy_port}')
        else:
            self.proxies = None

    def get(self, url):
        return requests.get(url=url, proxies=self.proxies, cookies=self.cookies)

converted_citations = []

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-x", "--proxy", 
                        help="port number on local machine to use for request proxy",
                        type=int)
    args = parser.parse_args()
    
    api_handler = None
    if args.proxy:
        print(f"Proxifying requests through socks5://0.0.0.0:{args.proxy}\n")
        api_handler = API(args.proxy)
    else:
        api_handler = API()

    clipboard = pc.paste()

    bib = bibtexparser.loads(clipboard)

    try:
        print(f"Converting {len(bib.entries)} documents.")
        
        for idx, entry in enumerate(tqdm(bib.entries)):
            if idx > 0:
                wait_time = random.randint(3, 10)
                time.sleep(wait_time)
                
            title = entry['title']
            base_url = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C5&q=" + title + "&btnG= "

            googleSearch = api_handler.get(base_url)
            
            bs_page = BeautifulSoup(googleSearch.content, "html.parser")
            block = bs_page.find("div", {"class": "gs_ri"})
            title = block.find("h3")
            link = title.find("a")
            citation_id = link["id"]

            cite_url = "https://scholar.google.com/scholar?hl=en&q=info:" + citation_id + ":scholar.google.com/&output=cite&scirp=0"

            findLatex = api_handler.get(cite_url)

            citation_view = BeautifulSoup(findLatex.content, "html.parser")
            latex_link = citation_view.find("div", {"id": "gs_citi"})

            latex_mf = latex_link.findChildren("a")[0]["href"]

            result = BeautifulSoup(api_handler.get(latex_mf).content, "html.parser")

            citation = bibtexparser.loads(result.text)

            if 'doi' in entry and 'doi' not in citation.entries[0]:
                citation.entries[0]['doi'] = entry['doi']

            converted_citations.append(bibtexparser.dumps(citation))

        out_text = '\n'.join(converted_citations)

        print(out_text)

        file_path = f"{os.getcwd()}/citescholar-{datetime.datetime.now()}.bib"

        with open(file_path, 'w+') as file:
            file.write(out_text)
            print(f"Result saved in {file_path}")

    except Exception as e:
        print('Cite conversion failed.')
        print(e)
        if len(converted_citations) > 0:
            print('\n'.join(converted_citations))