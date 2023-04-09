import os
from typing import Any, Optional, Callable
from atlassian import Confluence
from bs4 import BeautifulSoup
from operator import itemgetter
from projects.confluence.ConfluencePage import ConfluencePage
from projects.confluence.repositories.confluence import ConfluenceRepository

PageVisitorFunc = Callable[[ConfluencePage], None]


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

    # def get_pages_from_space(self, start=10, limit=20):
    #     pages = self.confluence.get_all_pages_from_space(space=self._confluence_space, start=start, limit=limit)
    #     for page in pages:
    #         print('=========================')
    #         print(page)

    # wip: get page content and child pages
    def visit_page_and_all_children(self, title: str, visitor: PageVisitorFunc):
        # get the page and its html content by expanding body.storage
        page = self.confluence.get_page_by_title(space=self._confluence_space, title=title, expand="body.storage")
        confluence_page = create_confluence_page_from_page_data(parent_page_id=None, page=page)
        visitor(confluence_page)
        self.recursively_visit_all_child_pages(confluence_page.page_id, visitor=visitor)

    # wip: get page children data.
    # todo: iterate over all children, recursively
    def recursively_visit_all_child_pages(self, page_id: str, visitor: PageVisitorFunc, start=0, limit=2, current_depth=0, max_depth=2000):
        # using pagination, get all child pages
        child_pages = self.confluence.get_page_child_by_type(page_id, type="page", start=start, limit=limit,
                                                             expand="body.storage")
        # visit each page so that the data is stored in the db
        # using recursion, get all child's children
        for child in child_pages:
            child_confluence_page = create_confluence_page_from_page_data(parent_page_id=page_id, page=child)
            visitor(child_confluence_page)
            self.recursively_visit_all_child_pages(page_id=child_confluence_page.page_id, visitor=visitor)

        # continue visiting direct children until pagination is exhausted.
        current_depth += 1
        if (len(child_pages) > 0) and current_depth <= max_depth:
            new_start = start + limit
            self.recursively_visit_all_child_pages(page_id=page_id, start=new_start, current_depth=current_depth,
                                                   max_depth=max_depth, visitor=visitor)

        if current_depth > max_depth:
            raise Exception(f'current_depth {current_depth} exceeded max depth {max_depth}')

    # test function, delete later
    def do_stuff(self):
        # self._repository.insertPage(page_id='1234', title='jason', parent_page_id='444123', web_url='https://jason.com', html_value='<body>hello<div>world</div></body>')
        self.visit_page_and_all_children(title='Core Services',
                                         visitor=lambda confluence_page: self.handle_page_visit(confluence_page))

    def handle_page_visit(self, confluence_page: ConfluencePage):
        # print(f'page visited: {confluence_page}')
        print(
            f'page by title: title: {confluence_page.title}, web_url: {confluence_page.web_url}, page_id: {confluence_page.page_id}')
        self._repository.insertPage(page_id=confluence_page.page_id, parent_page_id= confluence_page.parent_page_id,
                                    title=confluence_page.title, web_url=confluence_page.web_url,
                                    html_value=confluence_page.html_value)


# Get a strongly typed instance with the data we care about
def create_confluence_page_from_page_data(parent_page_id: str, page: Optional[Any]):
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
    return ConfluencePage(parent_page_id=parent_page_id, page_id=page_id, title=title, web_url=web_url, html_value=html_value)
