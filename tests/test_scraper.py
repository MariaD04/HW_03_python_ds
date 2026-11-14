import json
import os
import sys

import pytest
import requests

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import scraper  

BOOK_HTML = """
<html><body>
<ul class="breadcrumb"><li><a>Home</a></li><li><a>Books</a></li>
<li><a>Poetry</a></li><li class="active">A Light in the Attic</li></ul>
<article class="product_page">
<h1>A Light in the Attic</h1>
<p class="price_color">£51.77</p>
<p class="instock availability"><i></i> In stock (22 available) </p>
<p class="star-rating Three"></p>
<div id="product_description" class="sub-header"><h2>Product Description</h2></div>
<p>It's hard to imagine a world without A Light in the Attic.</p>
<table class="table table-striped">
<tr><th>UPC</th><td>a897fe39b1053632</td></tr>
<tr><th>Number of reviews</th><td>0</td></tr>
</table></article></body></html>
"""

LIST_HTML = """
<article class="product_pod"><h3><a href="book-a_1/index.html">A</a></h3></article>
<article class="product_pod"><h3><a href="book-b_2/index.html">B</a></h3></article>
"""

EXPECTED_KEYS = {'title', 'category', 'price', 'rating', 'availability',
                 'description', 'url', 'UPC'}


class FakeResponse:

    def __init__(self, text='', status_code=200):
        self.text = text
        self.status_code = status_code
        self.encoding = None

    def raise_for_status(self):
        if self.status_code >= 400:
            raise requests.HTTPError(str(self.status_code))


def test_get_book_data_returns_dict_with_keys(monkeypatch):
    monkeypatch.setattr(scraper.requests, 'get',
                        lambda *a, **k: FakeResponse(BOOK_HTML))
    data = scraper.get_book_data('http://x/book')
    assert isinstance(data, dict)
    assert EXPECTED_KEYS <= set(data)


def test_get_book_data_values(monkeypatch):
    monkeypatch.setattr(scraper.requests, 'get',
                        lambda *a, **k: FakeResponse(BOOK_HTML))
    data = scraper.get_book_data('http://x/book')
    assert data['title'] == 'A Light in the Attic'
    assert data['price'] == '£51.77'
    assert data['rating'] == 3
    assert data['availability'] == 22
    assert data['category'] == 'Poetry'
    assert data['UPC'] == 'a897fe39b1053632'


def test_scrape_books_collects_and_saves(monkeypatch, tmp_path):
    def fake_get(url, *args, **kwargs):
        if url.endswith('page-3.html'):
            return FakeResponse(status_code=404)
        return FakeResponse(LIST_HTML)

    monkeypatch.setattr(scraper.requests, 'get', fake_get)
    monkeypatch.setattr(scraper, 'get_book_data', lambda url: {'url': url})
    monkeypatch.chdir(tmp_path)

    books = scraper.scrape_books(is_save=True)
    assert len(books) == 4 
    assert books[0]['url'] == (
        'http://books.toscrape.com/catalogue/book-a_1/index.html')
    lines = (tmp_path / 'artifacts' / 'books_data.txt').read_text(encoding='utf-8').splitlines()
    assert len(lines) == 4
    assert json.loads(lines[0]) == books[0]


def test_scrape_books_no_save(monkeypatch, tmp_path):
    monkeypatch.setattr(scraper.requests, 'get',
                        lambda *a, **k: FakeResponse(status_code=404))
    monkeypatch.chdir(tmp_path)
    assert scraper.scrape_books(is_save=False) == []
    assert not (tmp_path / 'books_data.txt').exists()

    
def test_live_first_book():
    url = ('http://books.toscrape.com/catalogue/'
           'a-light-in-the-attic_1000/index.html')
    data = scraper.get_book_data(url)
    assert data['title'] == 'A Light in the Attic'
    assert data['price'] == '£51.77'
