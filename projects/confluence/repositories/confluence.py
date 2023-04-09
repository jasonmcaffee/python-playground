from psycopg2._psycopg import Column
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Date, text
from datetime import date

engine = create_engine('postgresql://jmcaffee:password@localhost:5432/postgres')
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

    def insertPage(self, page_id: str, title: str, parent_page_id: str, web_url: str, html_value: str):
        entry = ConfluencePageDbModel(page_id=page_id, title=title, updated_date=date.today(), web_url=web_url,
                                      parent_page_id=parent_page_id, html_value=html_value)
        self.session.add(entry)
        self.session.commit()

# from sqlalchemy import Column, String, Integer, Date, Table, ForeignKey
# from sqlalchemy.orm import relationship
#
# from base import Base
#
# movies_actors_association = Table(
#     'movies_actors', Base.metadata,
#     Column('movie_id', Integer, ForeignKey('movies.id')),
#     Column('actor_id', Integer, ForeignKey('actors.id'))
# )

# class Movie(Base):
#     __tablename__ = 'movies'
#
#     id = Column(Integer, primary_key=True)
#     title = Column(String)
#     release_date = Column(Date)
#     actors = relationship("Actor", secondary=movies_actors_association)
#
#     def __init__(self, title, release_date):
#         self.title = title
#         self.release_date = release_date


# from sqlalchemy import Column, String, Integer, Boolean, ForeignKey
# from sqlalchemy.orm import relationship, backref
#
# from base import Base
#
#
# class Stuntman(Base):
#     __tablename__ = 'stuntmen'
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     active = Column(Boolean)
#     actor_id = Column(Integer, ForeignKey('actors.id'))
#     actor = relationship("Actor", backref=backref("stuntman", uselist=False))
#
#     def __init__(self, name, active, actor):
#         self.name = name
#         self.active = active
#         self.actor = actor


# coding=utf-8
#
# # 1 - imports
# from datetime import date
#
# from actor import Actor
# from base import Session, engine, Base
# from contact_details import ContactDetails
# from movie import Movie
# from stuntman import Stuntman
#
# # 2 - generate database schema
# Base.metadata.create_all(engine)
#
# # 3 - create a new session
# session = Session()
#
# # 4 - create movies
# bourne_identity = Movie("The Bourne Identity", date(2002, 10, 11))
# furious_7 = Movie("Furious 7", date(2015, 4, 2))
# pain_and_gain = Movie("Pain & Gain", date(2013, 8, 23))
#
# # 5 - creates actors
# matt_damon = Actor("Matt Damon", date(1970, 10, 8))
# dwayne_johnson = Actor("Dwayne Johnson", date(1972, 5, 2))
# mark_wahlberg = Actor("Mark Wahlberg", date(1971, 6, 5))
#
# # 6 - add actors to movies
# bourne_identity.actors = [matt_damon]
# furious_7.actors = [dwayne_johnson]
# pain_and_gain.actors = [dwayne_johnson, mark_wahlberg]
#
# # 7 - add contact details to actors
# matt_contact = ContactDetails("415 555 2671", "Burbank, CA", matt_damon)
# dwayne_contact = ContactDetails("423 555 5623", "Glendale, CA", dwayne_johnson)
# dwayne_contact_2 = ContactDetails("421 444 2323", "West Hollywood, CA", dwayne_johnson)
# mark_contact = ContactDetails("421 333 9428", "Glendale, CA", mark_wahlberg)
#
# # 8 - create stuntmen
# matt_stuntman = Stuntman("John Doe", True, matt_damon)
# dwayne_stuntman = Stuntman("John Roe", True, dwayne_johnson)
# mark_stuntman = Stuntman("Richard Roe", True, mark_wahlberg)
#
# # 9 - persists data
# session.add(bourne_identity)
# session.add(furious_7)
# session.add(pain_and_gain)
#
# session.add(matt_contact)
# session.add(dwayne_contact)
# session.add(dwayne_contact_2)
# session.add(mark_contact)
#
# session.add(matt_stuntman)
# session.add(dwayne_stuntman)
# session.add(mark_stuntman)
#
# # 10 - commit and close session
# session.commit()
# session.close()

#
# # 1 - imports
# from datetime import date
#
# # other imports and sections...
#
# # 5 - get movies after 15-01-01
# movies = session.query(Movie) \
#     .filter(Movie.release_date > date(2015, 1, 1)) \
#     .all()
#
# print('### Recent movies:')
# for movie in movies:
#     print(f'{movie.title} was released after 2015')
# print('')
#
# # 6 - movies that Dwayne Johnson participated
# the_rock_movies = session.query(Movie) \
#     .join(Actor, Movie.actors) \
#     .filter(Actor.name == 'Dwayne Johnson') \
#     .all()
#
# print('### Dwayne Johnson movies:')
# for movie in the_rock_movies:
#     print(f'The Rock starred in {movie.title}')
# print('')
#
# # 7 - get actors that have house in Glendale
# glendale_stars = session.query(Actor) \
#     .join(ContactDetails) \
#     .filter(ContactDetails.address.ilike('%glendale%')) \
#     .all()
#
# print('### Actors that live in Glendale:')
# for actor in glendale_stars:
#     print(f'{actor.name} has a house in Glendale')
# print('')
