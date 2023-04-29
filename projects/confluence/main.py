from projects.confluence.services.ConfluenceAPI import ConfluenceAPI


def main():
    print('retrieving confluence pages and saving them to the db...')
    confluence = ConfluenceAPI()
    confluence.get_confluence_data_and_save_to_db(title='Contacts') # Corrections of Error
    print('process complete! All pages saved to the db!')


if __name__ == "__main__":
    main()
