import argparse
import os
import json
from pathlib import Path
from time import sleep
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import tqdm
from main import download_image, download_txt, check_for_redirect, parse_book_page, Url_Error


def find_last_page(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'lxml')
    return soup.select('.npage')[-1].text

def parse_category_page(category_url, page):
    url = f"{category_url}/{page}"
    response = requests.get(url)
    response.raise_for_status()
    check_for_redirect(response)
    soup = BeautifulSoup(response.text, 'lxml')
    book_tags = soup.select('.bookimage')
    book_links = [urljoin(url, book_tag.select_one('a')['href']) for book_tag in book_tags]
    return book_links


def get_category_books(book_url):
    folder_images = 'images'
    folder_txt = 'books'
    Path(folder_txt).mkdir(parents=True, exist_ok=True)
    Path(folder_images).mkdir(parents=True, exist_ok=True)
    books_tag = {}
    while True:
        try:
            book_id = book_url.split('/')[-2][1:]
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            soup = BeautifulSoup(response.text, 'lxml')
            books_tag[book_id] = parse_book_page(response.url, soup)
            download_image(books_tag[book_id]['book_name'], books_tag[book_id]['book_image_url'], folder_images, book_id)
            download_txt(books_tag[book_id]['book_name'], book_id, folder_txt)
            break
        except requests.HTTPError:
            break
        except requests.ConnectionError:
            sleep(10)
        except Url_Error:
            print('Нет книги для скачивания')
            break
    return books_tag


def save_json(books_tag, folder='.'):
    filename = 'category.json'
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(books_tag, file, ensure_ascii=False)


def create_parser(category_url):
    parser = argparse.ArgumentParser(description='Скрипт для скачивание книг с сайта https://tululu.org/')
    parser.add_argument('--start_page', nargs='?', default=1,
                        help='С какой страницы парсить', type=int)
    parser.add_argument('--end_page', nargs='?', default=find_last_page(category_url),
                        help='По какую страницу парсить', type=int)

    return parser


def main():
    category_url = "https://tululu.org/l55/"
    parser = create_parser(category_url)
    namespace = parser.parse_args()
    start_page, end_page = (namespace.start_page, namespace.end_page)
    links = [parse_category_page(category_url, page) for page in range(int(start_page), int(end_page))]

    book_links = [link for page in links for link in page]

    books_tag = [get_category_books(book_url) for book_url in tqdm(book_links)]
    save_json(books_tag)


if __name__ == "__main__":
    main()