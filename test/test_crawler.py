from tsg.crawler import crawl_site, crawl_urls, crawl_journal_url, crawl_journal_subsites
import os
import requests
from tsg.config import RAW_DIR

def test_crawl_journal():
    urls = ['http://dblp.uni-trier.de/db/journals/ij3dim/ij3dim1.html',
            'http://dblp.uni-trier.de/db/journals/ij3dim/ij3dim2.html',
            'http://dblp.uni-trier.de/db/journals/ij3dim/ij3dim3.html',
            'http://dblp.uni-trier.de/db/journals/ij3dim/ij3dim4.html']

    filenames = [RAW_DIR + 'journal_ij3dim_ij3dim1.html',
                 RAW_DIR + 'journal_ij3dim_ij3dim2.html',
                 RAW_DIR + 'journal_ij3dim_ij3dim3.html',
                 RAW_DIR + 'journal_ij3dim_ij3dim4.html']

    for f in filenames:
        try:
            os.remove(f)
        except OSError:
            pass
        assert not os.path.exists(f)

    crawl_journal_subsites('http://dblp.uni-trier.de/db/journals/ij3dim/')

    for i, url in enumerate(urls):
        with open(filenames[i]) as f:
            webpage = requests.get(url)
            assert f.read() == webpage.text

def test_crawl_journal_url():
    url = 'http://dblp.uni-trier.de/db/journals/crossroads/'
    url_journals = crawl_journal_url(url)
    assert url_journals[0][:2] == ['http://xrds.acm.org',
                                'http://dl.acm.org/citation.cfm?id=J1271']
    assert url_journals[1][:2] == ['http://dblp.uni-trier.de/db/journals/crossroads/crossroads22.html',
                                    'http://dblp.uni-trier.de/db/journals/crossroads/crossroads21.html']

def test_crawl_urls():
    url = 'http://dblp.uni-trier.de/pers?pos=1'
    urls = crawl_urls(url)
    assert len(urls) == 300
    assert 'http://dblp.uni-trier.de/pers/hd/a/A:Almaaf_Bader_Ali' in urls
    assert 'http://dblp.uni-trier.de/pers/hd/a/A:Ambha' in urls

    #Journals
    url_journals = 'http://dblp.uni-trier.de/db/journals/?pos=1'
    url_journals = crawl_urls(url_journals)
    assert len(url_journals) == 100
    assert url_journals[:2] == ['http://dblp.uni-trier.de/db/journals/ij3dim',
                                'http://dblp.uni-trier.de/db/journals/4or']
    assert url_journals[-1] == 'http://dblp.uni-trier.de/db/journals/jaif'

    # Conferences
    url_conferences = 'http://dblp.uni-trier.de/db/conf/?pos=1'
    url_conferences = crawl_urls(url_conferences)
    assert len(url_conferences) == 100

    assert url_conferences[:2] == ['http://dblp.uni-trier.de/db/conf/3dpvt',
                                   'http://dblp.uni-trier.de/db/conf/3dgis']
    assert 'http://dblp.uni-trier.de/db/conf/amcc' in url_conferences

def test_crawl_site():
    url = 'http://dblp.uni-trier.de/pers/hd/w/Walker:David'
    filename = RAW_DIR + 'author_w_Walker:David.html'

    crawl_site(url, 'author')

    webpage = requests.get(url)

    assert os.path.exists(filename)
    with open(filename) as f:
        assert f.read() == webpage.text


def test_crawl_site_html_suffix():
    url = 'http://dblp.uni-trier.de/db/journals/tap/tap7.html'
    filename = RAW_DIR + 'journal_tap_tap7.html'

    crawl_site(url, 'journal')

    webpage = requests.get(url)

    assert os.path.exists(filename)
    with open(filename) as f:
        assert f.read() == webpage.text
