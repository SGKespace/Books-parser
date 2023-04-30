import json
import argparse
import sys
from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from livereload import Server


PAGES_DIRECTORY = 'pages'


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    parser = argparse.ArgumentParser(description='Сайт для чтения книг, скачанных с https://tululu.org/.')
    parser.add_argument(
        '--json_path',
        nargs='?',
        type=Path,
        default='media/category.json',
        help='путь и имя файла о книгах .json'
    )
    parser.add_argument(
        '--books',
        nargs='?',
        type=int,
        default=20,
        help='количество книг на страницe'
    )
    parser_args = parser.parse_args()
    try:
        with open(parser_args.json_path, 'r', encoding='utf-8') as json_file:
            books_description = json.load(json_file)
    except FileNotFoundError as error:
        sys.exit(f'Неверно указан путь или имя файлаю Ошибка {error}')
    book_form = []
    for page in books_description:
        for book in page:
            book_form.insert(0, page[book])
    template = env.get_template('./template.html')
    Path(PAGES_DIRECTORY).mkdir(parents=True, exist_ok=True)
    books_description = list(chunked(book_form, parser_args.books))
    for page_number, books_page in enumerate(books_description, start=1):
        rendered_page = template.render(
            books_description=books_page,
            pages_number=len(books_description),
            page_number=page_number
        )
        with open(Path(PAGES_DIRECTORY).joinpath(f'index{page_number}.html'), 'w', encoding='utf8') as file:
            file.write(rendered_page)


def main():
    on_reload()


if __name__ == '__main__':
    main()


