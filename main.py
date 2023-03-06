import os
import urllib
from urllib.parse import urljoin
from pathvalidate import sanitize_filename
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import argparse


def main():
    parser = create_parser()
    args = parser.parse_args()
    folder_txt = 'books'
    folder_images = 'images'
    Path(folder_txt).mkdir(parents=True, exist_ok=True)
    Path(folder_images).mkdir(parents=True, exist_ok=True)

    # for book_id in range(args.start_id, args.end_id):
    for book_id in range(1, 10):
        url = f'https://tululu.org/b{book_id}/'
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'lxml')
        book = parse_book_page(response.url, soup)
        if book:
            title = book['book_name']
            img_url = book['book_image_url']

            download_txt_flag = True
            try:
                if download_txt_flag:
                    txt_filepath = download_txt(title, book_id, folder_txt)
                else:
                    txt_filepath = ''
            except requests.exceptions.HTTPError:
                print('Нет книги.  book_id: ', book_id)

            download_txt_flag = True
            try:
                if download_txt_flag:
                    img_filepath = download_image(title, img_url, folder_images, book_id)
                else:
                    img_filepath = ''
            except requests.exceptions.MissingSchema:
                print('Нет картинки.  book_id: ', book_id)




def create_parser():
    parser = argparse.ArgumentParser(description='Скрипт для скачивание книг с сайта https://tululu.org/')
    parser.add_argument('--start_id', nargs='?', default=1,
                        help='Начать с какого id книги парсить', type=int)
    parser.add_argument('--end_id', nargs='?', default=9999,
                        help='Закончить каким id книги парсить', type=int)
    return parser


def parse_book_page(url, soup):

    book_url = soup.find('a', text='скачать txt')
    if not book_url:
        return

    text_pars = soup.find(id="content").find('h1').text
    split_text = text_pars.split('::', maxsplit=1)
    author = split_text[1].strip()
    title = split_text[0].strip()
    title = sanitize_filename(title)

    book_txt_url = urljoin(url, book_url['href'])
    if not book_txt_url:
        return

    pars_img_url = soup.select_one('div .bookimage a img[src]')['src']
    img_url = urljoin(url, pars_img_url)

    book_comments = [comment.text for comment in soup.select('div.texts span.black')]

    book_genres = [genre.text for genre in soup.select('span.d_book a')]

    book = {
        'book_name': title,
        'book_author': author,
        'book_txt_url': book_txt_url if book_url else None,
        'book_image_url': img_url,
        'book_comments': book_comments,
        'book_genres': book_genres,
            }
    return book


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(title, book_id, folder):
    url = f"https://tululu.org/txt.php"
    params = {'id': book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    file_path = Path(f"./{folder}/{book_id}.{title}.txt")
    with file_path.open('wb') as file:
        file.write(response.content)
    return file_path


def download_image(title, img_url, folder_images, book_id):
    response = requests.get(img_url)
    response.raise_for_status()
    check_for_redirect(response)

    split_url = urllib.parse.urlsplit(img_url)
    full_path, full_name = os.path.split(split_url.path)
    file_name, file_extension = os.path.splitext(full_name)

    file_path = Path(f"./{folder_images}/{book_id}.{title}.{file_extension}")
    with file_path.open('wb') as file:
        file.write(response.content)
    return file_path


if __name__ == '__main__':
    main()