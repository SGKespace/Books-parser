from livereload import Server, shell
import render_website


server = Server()
server.watch('*.*', shell('render_website', cwd='.'))
server.serve(root='.')