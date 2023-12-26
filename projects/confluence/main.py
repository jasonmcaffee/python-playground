from src.data_downloaders.confluence.services.ConfluenceAPI import ConfluenceAPI
import time

def main():
    start_time = time.time()
    print('retrieving confluence pages and saving them to the db...')
    confluence = ConfluenceAPI()
    # confluence.get_confluence_data_and_save_to_db(title="Plaid Signal", confluence_space="EST")
    confluence.download_all_relevant_spaces()
    print(f'process complete! All pages saved to the db in {time.time() - start_time} !')
    # 30 seconds for entire SoFi Engineering documentation 2.0

if __name__ == "__main__":
    main()
