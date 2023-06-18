import pytest

from src.biquge.biquge5200 import Biquge5200
from src.log.log import LOGGER


class TestBiquge5200:
    """ Test class for Biquge5200 """
    @pytest.mark.parametrize('book_name', ['大明第一臣'])
    def test_search_book(self, book_name):
        """ Test search_book() method """
        book_info = Biquge5200().search_book(book_name)
        print(book_info)
        assert len(book_info) != 0

    def test_crawl_book_chapter_urls(self):
        """ Test crawl_book_chapter_urls() method """
        book_id = '154_154288'
        book, chapter_urls = Biquge5200().crawl_book_chapter_urls(book_id)
        print(book)
        assert book is not None
        assert chapter_urls is not None

    def test_crawl_chapter_title_content(self):
        """ Test crawl_chapter_title_content() method """
        chapter_url = 'http://www.biqu5200.net/154_154288/180608640.html'
        chapter_title_content = Biquge5200().crawl_chapter_title_content(chapter_url)
        print(chapter_title_content)
        assert chapter_title_content['title'] != 'Error title'

if __name__ == '__main__':
    pytest.main(['-v', '-s', 'test_biquge_5200.py'])