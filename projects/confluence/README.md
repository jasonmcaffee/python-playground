# Overview
Download confluence pages to a database.

Starting at the page title defined [here](https://github.com/jasonmcaffee/python-playground/blob/main/projects/confluence/main.py#L7), 
walk the children pages/nodes, doing depth first, and visit each page, then store the page data (title, page id, parent page id, and html) to the database.

Future iterations of this project can do threads/divide-and-conquer, along with batch updates, but for now simple sequential downloading works pretty well.

## Setup
### Chrome Web Driver
```shell
brew install chromedriver
cd /usr/local/Caskroom/chromedriver/116.0.5845.96/chromedriver-mac-x64/  
xattr -d com.apple.quarantine chromedriver
```

### pipenv install
Install dependencies defined in requirements.txt
```shell
pipenv install
```

### Environment Variables
create an .env file inside of /src/data_downloaders/confluence and add the following env vars.

e.g.
```shell
DB_CONNECTION=postgresql://postgres:postgrespw@localhost:50000/sofi_docs?options=--search_path%3Dconfluence
CONFLUENCE_BASE_URL=https://sofiinc.atlassian.net
CONFLUENCE_USERNAME=jmcaffee@sofi.org
CONFLUENCE_API_TOKEN=asdfasdf
```


#### DB_CONNECTION
connection string to your db 

e.g. `postgresql://jmcaffee:password@localhost:5432/postgres`
#### CONFLUENCE_BASE_URL
Your company's url for atlassian.

e.g. `https://company-name.atlassian.net`
#### CONFLUENCE_USERNAME
Your username for confluence.

e.g. `myname@mycompany.org`

#### CONFLUENCE_API_TOKEN
Token used to access confluence.

To create a token and get its value, go to [security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

![img.png](img.png)

### Intellij Configuration
Create a run configuration that points to main.py and sets the appropriate env vars.
![img_1.png](img_1.png)

### Database
Run the db setup script found [here](https://github.com/jasonmcaffee/python-playground/blob/main/projects/confluence/db/db_setup.sql)

It simply creates a new schema called 'confluence' and tables to house confluence date