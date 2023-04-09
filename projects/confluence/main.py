from projects.confluence.services.ConfluenceAPI import ConfluenceAPI


def main():
    print('main...')
    confluence = ConfluenceAPI()
    confluence.get_confluence_data_and_save_to_db()
    print('main complete!')


if __name__ == "__main__":
    main()
