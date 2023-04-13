import argparse
import os
import json
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
from main import check_for_redirect, get_books


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


def save_json(books_tag, json_path, folder):
    filename = f'{json_path}.json'
    filepath = os.path.join(folder, filename)
    with open(filepath, 'w', encoding='utf8') as file:
        json.dump(books_tag, file, ensure_ascii=False)


def create_parser(category_url):

    parser = argparse.ArgumentParser(description='Ввод диапазона страниц каталога книг')
    parser.add_argument('--start_page', nargs='?', default=700, help='С какой страницы парсить', type=int)
    parser.add_argument('--end_page', nargs='?',  default=find_last_page(category_url), help='По какую страницу парсить', type=int)
    parser.add_argument('-i', '--get_imgs', action='store_true', default=False, help='Cкачивать обложки книг')
    parser.add_argument('-t', '--get_txt', action='store_true', default=False, help='Cкачивать текст книг')
    parser.add_argument('-j', '--json_path', default='category', help='Указать свой путь к *.json файлу с результатами')
    parser.add_argument('-d', '--dest_folder', default='content/', help='Путь к каталогу с результатами парсинга: картинкам, книгами, json')

    return parser


def main():
    category_url = "https://tululu.org/l55/"
    parser = create_parser(category_url)
    namespace = parser.parse_args()
    start_page, end_page, get_imgs, get_txt, json_path, folder = (namespace.start_page, namespace.end_page,
                                           namespace.get_imgs, namespace.get_txt, namespace.json_path, namespace.dest_folder)
    Path(folder).mkdir(parents=True, exist_ok=True)
    links = [parse_category_page(category_url, page) for page in range(start_page,int(end_page))]
    book_links = [link for page in links for link in page]
    books_tag = [get_books(book_url, get_imgs, get_txt, folder) for book_url in tqdm(book_links)]
    save_json(books_tag, json_path, folder)


if __name__ == "__main__":
    main()