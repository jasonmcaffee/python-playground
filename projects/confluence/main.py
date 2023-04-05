from atlassian import Confluence
import os

# atlassian docs https://atlassian-python-api.readthedocs.io/
# confluence https://atlassian-python-api.readthedocs.io/confluence.html

# baseUrl = "https://sofiinc.atlassian.net"
baseUrl = os.getenv('CONFLUENCE_BASE_URL')  # https://mycomapny.atlassian.net

confluence_username = os.getenv('CONFLUENCE_USERNAME')  # myuser@mycompany.org
# to create a token go here https://id.atlassian.com/manage-profile/security/api-tokens
confluence_api_token = os.getenv('CONFLUENCE_API_TOKEN')  # Q33EKGJELblahblah


def main():
    print("running main!")
    # print(f'username: {confluence_username} token: {confluence_api_token}')
    confluence = Confluence(url=baseUrl, username=confluence_username, password=confluence_api_token)
    does_exist = confluence.page_exists(space="EST", title="Core Services")
    page_id = ""
    print(f'PageId is {page_id}')
    print(f'Does exist {does_exist}')
    print("done running main")


if __name__ == "__main__":
    main()
