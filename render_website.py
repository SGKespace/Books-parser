import json

from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from livereload import Server


PAGE_DIRECTORY = 'pages'


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('./template.html')

    books_path = Path.joinpath(Path.cwd().parents[0], 'lesson10/', 'category.json')
    with open(books_path, 'r', encoding='utf-8') as json_file:
        books = json.load(json_file)

    book_form = []
    for page in books:
        for book in page:
            book_form.insert(0, page[book])

    Path(PAGE_DIRECTORY).mkdir(parents=True, exist_ok=True)
    books = list(chunked(book_form, 20))
    for page_number, books_page in enumerate(books):
        rendered_page = template.render(
            books=books[page_number],
            pages_number=len(books),
            page_number=page_number
        )
        with open(Path(PAGE_DIRECTORY).joinpath(f'index{page_number + 1}.html'), 'w', encoding="utf8") as file:
            file.write(rendered_page)


def main():
    on_reload()
    server = Server()
    server.watch('*.html', on_reload)
    server.serve(root='.')


if __name__ == '__main__':
    main()