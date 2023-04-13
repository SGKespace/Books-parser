import argparse
import os
from pathlib import Path
from time import sleep
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from tqdm import tqdm


def get_books(book_url, get_imgs, get_txt, folder):
    books_tag = {}
    while True:
        try:
            book_id = book_url.split('/')[-2][1:]
            response = requests.get(book_url)
            response.raise_for_status()
            check_for_redirect(response)
            books_tag[book_id] = parse_book_page(
                response, book_url)
            if get_imgs:
                download_image(
                    books_tag[book_id]['Image'], str(book_id), folder)
            if get_txt:
                download_txt(books_tag[book_id]['Title'], book_id, folder)
            break
        except requests.HTTPError:
            print('Книга не найдена')
            break
        except requests.ConnectionError:
            print('Нет связи, повторная попытка через 2 сек.')
            sleep(2)
    return books_tag


def parse_book_page(response, url):
    soup = BeautifulSoup(response.text, 'lxml')
    author_title = soup.select_one('#content h1').text
    title, author = [name.strip() for name in author_title.split('::')]
    book_img = soup.select_one('div.bookimage img')['src']
    img_url = (urljoin(url, book_img))
    genres = [genre.text for genre in soup.select('span.d_book a')]
    comments = [comment.text for comment in soup.select('.texts span')]
    return {
        'Title': title,
        'Author': author,
        'Image': img_url,
        'Genres': genres,
        'Comments': comments
    }


def check_for_redirect(response):
    if response.history:
        print('Книги нет. Редирект на главную')
        raise requests.HTTPError


def get_file_ext(img_url):
    split_url = urlparse(img_url)
    return os.path.splitext(split_url.path)[-1]


def download_txt(title, book_id, folder):
    url = f"https://tululu.org/txt.php"
    params = {'id': book_id}
    response = requests.get(url, params=params)
    response.raise_for_status()
    check_for_redirect(response)
    filename = f"{book_id}.{title}.txt"
    filepath = os.path.join(folder, sanitize_filename(filename))
    with open(filepath, 'wb') as file:
        file.write(response.content)


def download_image(img_url, title, folder):
    response = requests.get(img_url)
    response.raise_for_status()
    check_for_redirect(response)
    file_ext = get_file_ext(img_url)
    filepath = os.path.join(folder, sanitize_filename(title) + file_ext)
    with open(filepath, 'wb') as file:
        file.write(response.content)


def create_parser():

    parser = argparse.ArgumentParser(description='Ввод диапазона ID книг')
    parser.add_argument('--start_id', nargs='?', default=1, help='С какого ID парсить', type=int)
    parser.add_argument('--end_id', nargs='?', default=9999, help='По какой ID парсить', type=int)
    parser.add_argument('-i', '--get_imgs', action='store_true', default=False, help='Cкачивать обложки книг')
    parser.add_argument('-t', '--get_txt', action='store_true', default=False, help='Cкачивать текст книг')
    parser.add_argument('-d', '--dest_folder', default='content/', help='Путь к каталогу с результатами парсинга: картинкам, книгами, json')

    return parser


def main():
    parser = create_parser()
    namespace = parser.parse_args()
    start_id, end_id, get_imgs, get_txt, folder = (namespace.start, namespace.end,
                                                   namespace.get_imgs, namespace.get_txt, namespace.dest_folder)
    Path(folder).mkdir(parents=True, exist_ok=True)
    books_tag = [get_books(f"https://tululu.org/b{book_id}/", get_imgs, get_txt, folder) for book_id in
                 tqdm(range(start_id, end_id + 1), desc="Собираем книжки")]


if __name__ == "__main__":
    main()