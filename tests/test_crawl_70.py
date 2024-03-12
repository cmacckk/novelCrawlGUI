import pytest

from src.biquge.biquge70 import Biquge70


class TestBiquge70:
    """ Test class for Biquge70 """
    @pytest.mark.parametrize('book_name', ['武侠'])
    def test_search_book(self, book_name):
        """ Test search_book() method """
        book_info = Biquge70().search_by_drission_page(book_name)
        print(book_info)
        assert book_info is not None


if __name__ == '__main__':
    pytest.main(['-v', '-s', 'test_biquge70.py'])