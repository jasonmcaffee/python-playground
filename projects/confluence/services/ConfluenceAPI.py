import os
from typing import Any, Optional
from atlassian import Confluence
from bs4 import BeautifulSoup
from operator import itemgetter
from projects.confluence.ConfluencePage import ConfluencePage
from projects.confluence.repositories.confluence import ConfluenceRepository


# Singleton wrapper/helper for confluence api
# https://python-patterns.guide/gang-of-four/singleton/
# https://atlassian-python-api.readthedocs.io/
# https://atlassian-python-api.readthedocs.io/confluence.html
# https://docs.atlassian.com/ConfluenceServer/rest/8.2.0/#api/content-getContentById
# BeautifulSoup for converting raw html, returned by confluence, to text.
# It also provides a query-esque api for finding elements
# https://www.geeksforgeeks.org/converting-html-to-text-with-beautifulsoup/
# https://www.crummy.com/software/BeautifulSoup/bs4/doc/
class ConfluenceAPI:
    _instance = None
    _confluence_space = "EST"
    _repository: ConfluenceRepository = ConfluenceRepository()

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
        # _repository = ConfluenceRepository()

    def get_pages_from_space(self, start=10, limit=20):
        pages = self.confluence.get_all_pages_from_space(space=self._confluence_space, start=start, limit=limit)
        for page in pages:
            print('=========================')
            print(page)

    # wip: get page content and child pages
    def get_page_by_title(self, title: str):
        # get the page and its html content by expanding body.storage
        page = self.confluence.get_page_by_title(space=self._confluence_space, title=title, expand="body.storage")
        print(page)
        confluence_page = create_confluence_page_from_page_data(page)
        print(
            f'page by title: title: {confluence_page.title}, web_url: {confluence_page.web_url}, page_id: {confluence_page.page_id}')
        self.get_all_child_pages(confluence_page.page_id)

    # wip: get page children data.
    # todo: iterate over all children, recursively
    def get_all_child_pages(self, page_id: str, start=0, limit=2, current_depth=0, max_depth=2):
        child_pages = self.confluence.get_page_child_by_type(page_id, type="page", start=start, limit=limit,
                                                             expand="body.storage")
        for child in child_pages:
            child_confluence_page = create_confluence_page_from_page_data(child)
            print(f'child page title: {child_confluence_page.title}')

        current_depth += 1
        if (len(child_pages) > 0) and current_depth <= max_depth:
            print(f'getting more child pages')
            new_start = start + limit
            self.get_all_child_pages(page_id=page_id, start=new_start, current_depth=current_depth, max_depth=max_depth)

    # test function, delete later
    def do_stuff(self):
        self._repository.insertPage(page_id='1234', title='jason', parent_page_id='444123', web_url='https://jason.com', html_value='<body>hello<div>world</div></body>')
        # self.get_page_by_title(title='Core Services')


# Get a strongly typed instance with the data we care about
def create_confluence_page_from_page_data(page: Optional[Any]):
    page_id, title, links = itemgetter('id', 'title', '_links')(page)
    html_value = page.get('body', {}).get('storage', {}).get('value', None)
    web_url = links.get('webui', None)
    # print(f'page_id: {page_id}, title: {title}, web_url: {web_url},')
    # print(f'html_value: {html_value}')
    # # convert the html to text
    # page_soup = BeautifulSoup(html_value, "html.parser")
    # page_as_text = page_soup.get_text()
    # # print(f'page is {page}')
    # print(f'page content is {page_as_text}')
    return ConfluencePage(page_id=page_id, title=title, web_url=web_url, html_value=html_value)
