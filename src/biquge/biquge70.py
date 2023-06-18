import requests
from urllib.parse import urlparse
from lxml import etree
from urllib.parse import urljoin, urlparse
from multiprocessing import Pool
from tqdm import tqdm

import json
from src.utils.get_user_agent import generate_random_user_agent
from src.config.config import TIMEOUT
from src.log.log import LOGGER


class Biquge70:
    """ site url: https://www.bqg70.com/ """
    def search_book(self, book):
        """ search book

            Returns:
                book_info: list[{'book': 'book name',
                                 'book_id': 'book id',
                                 'author': 'author',
                                 'source': 'source'}]
        """
        headers = {"User-Agent": generate_random_user_agent()}
        response = requests.get(url='https://m.bqgso.cc/search_json?q=' + book,
                                headers=headers,
                                timeout=TIMEOUT)
        html_content = response.content.decode('utf-8')

        info_json = json.loads(html_content)

        book_info = []

        # return book info
        for i, data in enumerate(info_json):
            if data['url_list'].endswith('/'):
                book_id = urlparse(data['url_list']).path.split('/')[-2]
            else:
                book_id = urlparse(data['url_list']).path.split('/')[-1]
            book_info.append(
                {
                    'book': data['articlename'],
                    'book_id': book_id,
                    'author': data['author'],
                    'source': 'bqg70'
                }
            )
        return book_info

    def crawl_book_chapter_urls(self, book_url):
        """ get book name and chapter urls """
        parsed = urlparse(book_url)
        url = parsed.scheme + "://" + parsed.netloc

        response = requests.get(book_url, headers={
                                "User-Agent": generate_random_user_agent()})

        html_content = response.content.decode('utf-8')
        xml = etree.HTML(html_content)
        book_name = xml.xpath('//span[@class="title"]/text()')
        book_chapter_url_path = xml.xpath('//dd/a/@href')

        book_chapter_url_list = []

        for path in book_chapter_url_path:
            if "book" in path:
                book_chapter_url_list.append(urljoin(url, path))
        return book_name, book_chapter_url_list

    def crawl_chapter_title_content(self, url):
        """ get single chapter title and content """
        result = ""
        response = requests.get(
            url,
            headers={"User-Agent": generate_random_user_agent()},
            timeout=TIMEOUT)
        html = response.content.decode('utf-8')
        xml = etree.HTML(html)
        title = xml.xpath('//span[@class="title"]/text()')
        content = xml.xpath('//div[@id="chaptercontent"]/text()')
        for data in content:
            result += data.replace("\u3000", "") + '\n'

        return {
            "title": title[0].split('_')[0],
            "content": result.rstrip()
        }

    def craw_book(self, book_url, thread=10, path='./'):
        """ crawl book """
        book, book_chapter_url_list = self.crawl_book_chapter_urls(book_url)

        with Pool(thread) as p:
            all_chapter_content = list(tqdm(p.imap(self.crawl_chapter_title_content,
                                     book_chapter_url_list[:-10]), total=len(book_chapter_url_list[:-10])))

        with open(path + book[0] + '.txt', "w", encoding='utf-8') as file:
            for chapter in all_chapter_content:
                file.write(chapter['title'] + '\n\n' +
                           chapter['content'] + '\n')
