# Overview
Download confluence pages to a database

## Setup
### Environment Variables
#### CONFLUENCE_BASE_URL
Your company's url for atlassian.

e.g. https://company-name.atlassian.net
#### CONFLUENCE_USERNAME
Your username for confluence.

e.g. myname@mycompany.org

#### CONFLUENCE_API_TOKEN
Token used to access confluence.

To create a token and get its value, go to [security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

![img.png](img.png)

### Intellij Configuration
Create a run configuration that points to main.py and sets the appropriate env vars.
![img_1.png](img_1.png)