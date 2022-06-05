#!/usr/bin/python3

import logging

def build_logger():
    file_handler = logging.FileHandler('nerd_fonts.log')
    logger = logging.getLogger('logger')
    logger.setLevel(level=logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger

def gets_urls_list():
    from bs4 import BeautifulSoup
    from requests import get

    URL = 'https://www.nerdfonts.com/font-downloads'
    response = get('http://www.nerdfonts.com/font-downloads')
    logger.info('response: %s' % response.status_code)
    sopa = BeautifulSoup(response.text, 'html.parser')
    urls = sopa.find_all(href=True)
    links = []
    for link in urls:
        links.append(link.get('href'))
        logger.info('link found it \n%s' % link.get('href'))
    return links

def clean_urls_list(links):
    zips = []
    for link in links:
        if link[-3:] == 'zip':
            zips.append(link)
            logger.info('zip found it \n%s' % link)
    return list(set(zips)) 

def download_fonts(clean_urls_list):
    logger.info('list have %s items' % len(clean_urls_list))
    for url in clean_urls_list:
        logger.info(url)
    from wget import download

    for index, url in enumerate(clean_urls_list):
        print('link ',index , ' ', url) 
        download(url)

if __name__ == '__main__':
    logger = build_logger()
    download_fonts(clean_urls_list(gets_urls_list()))
