import os

from psycopg2._psycopg import Column
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Date, text
from datetime import date
db_connection = os.getenv('DB_CONNECTION')
engine = create_engine(db_connection)
Session = sessionmaker(bind=engine)
Base = declarative_base()


class ConfluencePageDbModel(Base):
    __tablename__ = 'confluence_page'

    page_id = Column(String, primary_key=True)
    title = Column(String)
    updated_date = Column(Date)
    web_url = Column(String)
    parent_page_id = Column(String)
    html_value = Column(String)

    def __init__(self, page_id, title, updated_date, parent_page_id, web_url, html_value):
        self.page_id = page_id
        self.title = title
        self.updated_date = updated_date
        self.parent_page_id = parent_page_id
        self.web_url = web_url
        self.html_value = html_value


class ConfluenceRepository:
    def __init__(self):
        self.session = Session()
        self.session.execute(text("set schema 'confluence'"))

    def insert_page(self, page_id: str, title: str, parent_page_id: str, web_url: str, html_value: str):
        entry = ConfluencePageDbModel(page_id=page_id, title=title, updated_date=date.today(), web_url=web_url,
                                      parent_page_id=parent_page_id, html_value=html_value)
        self.session.add(entry)
        self.session.commit()

