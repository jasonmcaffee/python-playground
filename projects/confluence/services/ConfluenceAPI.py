import os
from atlassian import Confluence
from bs4 import BeautifulSoup


# Singleton wrapper/helper for confluence api
# https://python-patterns.guide/gang-of-four/singleton/
# https://atlassian-python-api.readthedocs.io/
# https://atlassian-python-api.readthedocs.io/confluence.html
# BeautifulSoup for converting raw html, returned by confluence, to text.
# It also provides a query-esque api for finding elements
# https://www.geeksforgeeks.org/converting-html-to-text-with-beautifulsoup/
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
class ConfluenceAPI:
    _instance = None
    _confluence_space = "EST"

    def __new__(cls):
        if cls._instance is None:
            print('instantiating object')
            cls._instance = super(ConfluenceAPI, cls).__new__(cls)
            cls._instance._init_confluence()
        return cls._instance

    def _init_confluence(self):
        print('init confluence called')
        base_url = os.getenv('CONFLUENCE_BASE_URL')
        username = os.getenv('CONFLUENCE_USERNAME')
        api_token = os.getenv('CONFLUENCE_API_TOKEN')
        self.confluence = Confluence(url=base_url, username=username, password=api_token)

    def does_page_exist(self, page_title: str = 'Core Services'):
        return self.confluence.page_exists(space=self._confluence_space, title=page_title)

    def get_pages_from_space(self, start=10, limit=20):
        pages = self.confluence.get_all_pages_from_space(space=self._confluence_space, start=start, limit=limit)
        for page in pages:
            print('=========================')
            print(page)

    def get_page_by_title(self, title: str):
        page = self.confluence.get_page_by_title(space=self._confluence_space, title=title, expand="body.storage")
        html_value = page.get('body', {}).get('storage', {}).get('value', None)
        page_soup = BeautifulSoup(html_value, "html.parser")
        page_as_text = page_soup.get_text()
        # print(f'page is ${page}')
        print(f'page content is {page_as_text}')
        print(f'page html is {html_value}')

    # test function, delete later
    def do_stuff(self):
        self.get_page_by_title(title='Core Services')
