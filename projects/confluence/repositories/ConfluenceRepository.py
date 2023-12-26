import os

from psycopg2._psycopg import Column
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Date, text
from sqlalchemy.dialects.postgresql import insert
from datetime import date
from dotenv import load_dotenv
load_dotenv()

db_connection = os.getenv('DB_CONNECTION')
engine = create_engine(db_connection)
# Session = sessionmaker(bind=engine)
Base = declarative_base()
SessionLocal = scoped_session(sessionmaker(bind=engine))


class ConfluencePageDbModel(Base):
    __tablename__ = 'confluence_page'

    page_id = Column(String, primary_key=True)
    title = Column(String)
    updated_date = Column(Date)
    web_url = Column(String)
    parent_page_id = Column(String)
    html_value = Column(String)
    space = Column(String)

    def __init__(self, page_id, title, updated_date, parent_page_id, web_url, html_value, space):
        self.page_id = page_id
        self.title = title
        self.updated_date = updated_date
        self.parent_page_id = parent_page_id
        self.web_url = web_url
        self.html_value = html_value
        self.space = space


class ConfluenceRepository:
    def insert_page(self, page_id: str, title: str, parent_page_id: str, web_url: str, html_value: str, space: str):
        session = SessionLocal() # new session needed each time or you'll get commit errors from multi threading
        statement = insert(ConfluencePageDbModel).values(
            page_id=page_id,
            title=title,
            updated_date=date.today(),
            web_url=web_url,
            parent_page_id=parent_page_id,
            html_value=html_value,
            space=space
        )
        on_conflict_statement = statement.on_conflict_do_update(
            index_elements=['page_id'],  # Specify the column(s) that uniquely identify a row
            set_={
                'title': title,
                'updated_date': date.today(),
                'web_url': web_url,
                'parent_page_id': parent_page_id,
                'html_value': html_value,
                'space': space,
            }
        )
        session.execute(on_conflict_statement)
        session.commit()
        session.close()

