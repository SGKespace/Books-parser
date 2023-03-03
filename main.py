import os
import requests
import urllib
from pathvalidate import sanitize_filename
from pathlib import Path


def main():
    folder = 'books'
    title = 'examination'
    Path(folder).mkdir(parents=True, exist_ok=True)

    for book_id in range(10):
        download_txt_flag = True
        try:
            if download_txt_flag:
                txt_filepath = download_txt(title, book_id, folder)
            else:
                txt_filepath = ''
            print(book_id, txt_filepath)
        except requests.exceptions.HTTPError:
            print('Неn такого book_id: ', book_id)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(title, book_id, folder):
    url = f"https://tululu.org/txt.php"
    params = {'id': book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    file_path = Path(f"./{folder}/{book_id}_{title}.txt")
    with file_path.open('wb') as file:
        file.write(response.content)
    return file_path


if __name__ == '__main__':
    main()