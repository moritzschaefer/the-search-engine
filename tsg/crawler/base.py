from lxml import html
import re
import os
import logging
from tsg.config import RAW_DIR
from tsg.crawler.downloader import get_site


def crawl_site(url, category):
    logging.info('Downloading URL {}'.format(url))
    url_parts = re.search('([^/]*)/([^/]*)$', url).groups()
    filename = '{}_{}_{}{}'.format(category,
                                   url_parts[0],
                                   url_parts[1],
                                   '' if url_parts[1][-5:] == '.html'
                                   else'.html')

    doc_path = RAW_DIR + filename
    if os.path.isfile(doc_path):
        logging.warn('File {} exists already. Skipping'.format(doc_path))
        return

    webpage = get_site(url)
    with open(doc_path, 'w') as f:
        f.write(webpage.text)

def crawl_journal(journal_url):
    logging.info('Downloading URL {}'.format(journal_url))
    journal_site = get_site(journal_url)
    tree = html.fromstring(journal_site.content)
    journal_info_links = tree.xpath("//div[@id='main']/p/a/@href")
    journal_volume_links = tree.xpath("//div[@id='main']/ul/li/a/@href")
    journal_links = [journal_info_links,journal_volume_links]
    return journal_links


def crawl_urls(url):

    logging.info('Downloading URL {}'.format(url))
    webpage = get_site(url)
    tree = html.fromstring(webpage.content)
    links = tree.xpath("//div[contains(@id,'output')]//ul/li/a/@href")
    return links


def crawl_loop(category, n=1):

    if category == 'journal':
        url = 'http://dblp.uni-trier.de/db/journals/?pos={}'
        pagination = 100
    elif category == 'author':
        url = 'http://dblp.uni-trier.de/pers?pos={}'
        pagination = 300
    elif category == 'conference':
        url = 'http://dblp.uni-trier.de/db/conf/?pos={}'
        pagination = 100
    else:
        raise ValueError('category must have one of the three!')

    while True:
        links = crawl_urls(url.format(str(n)))
        if len(links) < 1:
            logging.warn('Didn\' find any links')
            break
        for link in links:
            crawl_site(link, category)
        n += pagination
    return n
