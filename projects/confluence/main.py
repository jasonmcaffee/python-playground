from projects.confluence.services.ConfluenceAPI import ConfluenceAPI


def main():
    print('main...')
    confluence = ConfluenceAPI()
    confluence.do_stuff()
    print('main complete!')


if __name__ == "__main__":
    main()
