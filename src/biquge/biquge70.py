import requests
from urllib.parse import urlparse, quote
from lxml import etree
from urllib.parse import urljoin
from multiprocessing import Pool
from tqdm import tqdm
import time

from DrissionPage import WebPage, ChromiumOptions
from DrissionPage.errors import ElementNotFoundError
from DrissionPage.common import By

import json
from src.utils.get_user_agent import generate_random_user_agent
from src.config.config import TIMEOUT
from src.log.log import LOGGER


class Biquge70:
    """ site url: https://www.bqg70.com/ """
    
    def search_by_drission_page(self, book_name):
        """ Use DrissionPage func to crawl book information """
        LOGGER.info("Search book %s", book_name)
        chromium_options = ChromiumOptions()
        chromium_options.set_argument('--headless')
        page = WebPage(driver_or_options=chromium_options)
        page.get('https://www.bqg70.com/')
        page.ele('@name=q').input(book_name)
        page.ele('@type=submit').click()
        loop = 5
        page.wait.load_start()
        try:
            for index in range(loop):
                div = page.ele('@class=hots', timeout=4)
                if div.text == '加载中……':
                    LOGGER.info('Loading search result, wait 2s, try %s', index + 1)
                    time.sleep(2)
                else:
                    break
            if div.text == '暂无':
                return '暂时无法使用搜索功能'
        except ElementNotFoundError:
            LOGGER.info('Loading over...')

        authors_loc = (By.XPATH, '//div[@class="author"]')
        book_names_loc = (By.XPATH, '//h4[@class="bookname"]/a')

        authors = page.eles(authors_loc)
        book_names = page.eles(book_names_loc)

        book_info = []
        for index, name in enumerate(book_names):
            book_info.append(
                {'book': name.text,
                'book_id': name.link.split('/')[-2],
                'author': authors[index].text.split('：')[-1],
                'source': 'bqg70'}
            )
        page.close_driver()
        return book_info

    def search_book(self, book):
        """ search book

            Returns:
                book_info: list[{'book': 'book name',
                                 'book_id': 'book id',
                                 'author': 'author',
                                 'source': 'source'}]
        """
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                                 'Chrome/114.0.0.0 Safari/537.36',
                   }
        response = requests.get(url='https://www.bqg70.com/user/search.html?q=' + quote(book),
                                headers=headers,
                                timeout=TIMEOUT,)
        print(response)
        html_content = response.content.decode('utf-8')

        info_json = json.loads(html_content)

        book_info = []

        try:
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
        except TypeError as error:
            LOGGER.error(error)
            return


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
                                                   book_chapter_url_list[:-10]),
                                            total=len(book_chapter_url_list[:-10])))

        with open(path + book[0] + '.txt', "w", encoding='utf-8') as file:
            for chapter in all_chapter_content:
                file.write(chapter['title'] + '\n\n' +
                           chapter['content'] + '\n')
