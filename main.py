import os
import urllib
from pathvalidate import sanitize_filename
from pathlib import Path
import requests
from bs4 import BeautifulSoup



def main():
    for book_id in range(11):
        title, author = book_info(book_id)
        download_books(book_id, title)


def book_info(book_id):
    url = f'https://tululu.org/b{book_id}/'
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    try:
        text_pars = soup.find(id="content").find('h1').text
        split_text = text_pars.split('::', maxsplit=1)
        author = split_text[1].strip()
        title = split_text[0].strip()
    except AttributeError:
        author = None
        title = None

    print('Загаловок: ', title)
    print('Автор: ', author)
    return title, author


def download_books(book_id, title):  # это все уйдет в main() без функции
    folder = 'books'
    Path(folder).mkdir(parents=True, exist_ok=True)
    download_txt_flag = True
    try:
        if download_txt_flag:
            txt_filepath = download_txt(title, book_id, folder)
        else:
            txt_filepath = ''
        print(book_id)
        print(txt_filepath)
    except requests.exceptions.HTTPError:
        print('Нет книги.  book_id: ', book_id)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(title, book_id, folder):
    url = f"https://tululu.org/txt.php"
    params = {'id': book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    title = sanitize_filename(title)
    file_path = Path(f"./{folder}/{book_id}.{title}.txt")
    with file_path.open('wb') as file:
        file.write(response.content)
    return file_path


if __name__ == '__main__':
    main()