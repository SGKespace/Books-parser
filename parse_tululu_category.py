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


def main():
    category_url = "https://tululu.org/l55/"
    last_page = 4
    links = [parse_category_page(category_url, page) for page in range(1, int(last_page)+1)]
    book_links = [link for page in links for link in page]

    books_tag = [get_category_books(book_url) for book_url in tqdm(book_links)]
    save_json(books_tag)


if __name__ == "__main__":
    main()