import os
from typing import Any, Optional, Callable
from atlassian import Confluence
from bs4 import BeautifulSoup
from operator import itemgetter
from projects.confluence.ConfluencePage import ConfluencePage
from projects.confluence.repositories.confluence import ConfluenceRepository

# Type definition of a function which accepts a ConfluencePage and has no return.
# Useful for storing page data to the db when each page is visited/retrieved.
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
# TODO: divide and conquer using threads and batch inserts
class ConfluenceAPI:
    _instance = None
    _confluence_space = "EST"
    _repository: ConfluenceRepository = ConfluenceRepository()

    def __new__(cls):
        if cls._instance is None: # singleton implementation
            cls._instance = super(ConfluenceAPI, cls).__new__(cls)
            cls._instance._init_confluence()
        return cls._instance

    def _init_confluence(self):
        base_url = os.getenv('CONFLUENCE_BASE_URL')
        username = os.getenv('CONFLUENCE_USERNAME')
        api_token = os.getenv('CONFLUENCE_API_TOKEN')
        self.confluence = Confluence(url=base_url, username=username, password=api_token)

    # wip: get page content and child pages
    def visit_page_and_all_children(self, title: str, visitor: PageVisitorFunc):
        """
        Visits the page with the specified title and recursively iterates over all child pages.
        :param title: Title of the confluence page. e.g. "Communications Platform"
        :param visitor: lambda which accepts a ConfluencePage.  Typically used to store the page to the db.
        :return:
        """
        # get the page and its html content by expanding body.storage
        page = self.confluence.get_page_by_title(space=self._confluence_space, title=title, expand="body.storage")
        confluence_page = create_confluence_page_from_page_data(parent_page_id=None, page=page)
        visitor(confluence_page)
        self.recursively_visit_all_child_pages(confluence_page.page_id, visitor=visitor)

    def recursively_visit_all_child_pages(self, page_id: str, visitor: PageVisitorFunc, start=0, limit=20,):
        """
        Retrieve all direct child pages of the page_id, then iterate over each, finding their child pages, in a depth first manner.
        Visitor function is called as each page is retrieved, which then saves the data to the db.
        :param page_id: page id used by confluence
        :param visitor: lambda which accepts a ConfluencePage.  Typically used to store the page to the db.
        :param start: for confluence api pagination
        :param limit: for confluence api pagination
        :return:
        """
        # using pagination, get all child pages
        try:
            child_pages = self.confluence.get_page_child_by_type(page_id, type="page", start=start, limit=limit,
                                                                 expand="body.storage")
        except Exception as e:  # e.g. There is no content with the given id, or the calling user does not have permission to view the content
            print(f'unable to get child pages of page_id: {page_id} due to exception: {str(e)}')
            return

        # visit each page so that the data is stored in the db
        # using recursion, get all child's children
        for child in child_pages:
            child_confluence_page = create_confluence_page_from_page_data(parent_page_id=page_id, page=child)
            visitor(child_confluence_page)
            self.recursively_visit_all_child_pages(page_id=child_confluence_page.page_id, visitor=visitor)

        # continue visiting direct children until pagination is exhausted.
        if len(child_pages) > 0:
            new_start = start + limit
            self.recursively_visit_all_child_pages(page_id=page_id, start=new_start, visitor=visitor)

    def get_confluence_data_and_save_to_db(self, title: str):
        """
        Main entry point for starting at the Confluence page with the specified title, then recursively walking all children,
        storing each page into the db.
        :param title: The Confluence page title to start at.
        :return:
        """
        self.visit_page_and_all_children(title=title,
                                         visitor=lambda confluence_page: self._handle_page_visit(confluence_page))

    def _handle_page_visit(self, confluence_page: ConfluencePage):
        """
        Each time a page or child page data is retrieved, this function is called, and we store the page information to the db.
        :param confluence_page:
        :return:
        """
        print(
            f'page by title: title: {confluence_page.title}, web_url: {confluence_page.web_url}, page_id: {confluence_page.page_id}')
        self._repository.insert_page(page_id=confluence_page.page_id, parent_page_id=confluence_page.parent_page_id,
                                     title=confluence_page.title, web_url=confluence_page.web_url,
                                     html_value=confluence_page.html_value)


# Get a strongly typed instance with the data we care about
def create_confluence_page_from_page_data(parent_page_id: str, page: Optional[Any]):
    page_id, title, links = itemgetter('id', 'title', '_links')(page)
    html_value = page.get('body', {}).get('storage', {}).get('value', None)
    web_url = links.get('webui', None)
    return ConfluencePage(parent_page_id=parent_page_id, page_id=page_id, title=title, web_url=web_url,
                          html_value=html_value)

# def get_pages_from_space(self, start=10, limit=20):
#     pages = self.confluence.get_all_pages_from_space(space=self._confluence_space, start=start, limit=limit)
#     for page in pages:
#         print('=========================')
#         print(page)
