create schema if not exists confluence;

set schema 'confluence';

create table confluence_page (
    page_id varchar(255) primary key,
    html_value text,
    title varchar(255),
    web_url varchar(600),
    updated_date timestamp,
    parent_page_id varchar (255)
);