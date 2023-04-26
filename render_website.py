import json
# import collections

# from http.server import HTTPServer, SimpleHTTPRequestHandler
# from environs import Env
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from livereload import Server


def on_reload():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('./template.html')

    books_path = Path.joinpath(Path.cwd().parents[0], 'lesson10/content/', 'category.json')
    with open(books_path, 'r', encoding='utf-8') as json_file:
        books = json.load(json_file)
    book_form=[]
    for page in books:
        for book in page:
            book_form.insert(0, page[book])

    # books_set = collections.defaultdict(list)
    rendered_page = template.render(
        books=book_form
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)

def main():
    on_reload()
    server = Server()
    server.watch('*.html', on_reload)
    server.serve(root='.')

    # server = HTTPServer(('0.0.0.0', 8000), SimpleHTTPRequestHandler)
    # server.serve_forever()


if __name__ == '__main__':
    main()