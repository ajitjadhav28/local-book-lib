from flask import Flask, jsonify, request, render_template
from db_update import SQL_DB_NAME, BOOKS_CREATE_VIRTUAL_TABLE
import os, functools, argparse, logging, sqlite3
from flask_cors import CORS
from term_colors import bcolors
import urllib

app = Flask(__name__, template_folder=os.path.abspath('./build'), static_folder=os.path.abspath('./build/static'))
cors = CORS(app)

search_query = "SELECT url FROM books_virtual WHERE books_virtual MATCH '{}' ORDER BY RANK, year DESC;"
conn = None

def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def query_databse(query, query_format):
    try:
        results = conn.execute(query_format.format(query))
    except Exception as e:
        logging.error(str(e))
        return []
    return results.fetchall()


def searc_database(query, format_query):
    book_query = 'SELECT * FROM books WHERE url IN {};'
    try:
        results = conn.execute(format_query.format(query))
    except Exception as e:
        logging.debug('Exception occured while searching virtual database.')
        logging.error(str(e))
        return []
    books = []
    urls = "("
    logging.debug(format_query)
    for url in results.fetchall():
        logging.debug(url)
        urls += '"' + url['url'] + '",' if len(url) else ''
    if urls[-1] == ',':
        urls = urls[0:-1]
    urls += ")"
    try:
        books = conn.execute(book_query.format(urls)).fetchall()
    except Exception as e:
        logging.debug('Exception occured while querying books.')
        logging.error(str(e))
    return books


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<search>', methods=['POST'])
@functools.lru_cache(maxsize=100)
def search(search):
    search = urllib.parse.unquote(search)
    logging.info(bcolors.color('SEARCH: ', bcolors.lightcyan) + search)
    if request.method == 'POST' and len(search) > 0 :
        return jsonify(searc_database(search, search_query))

@app.route('/suggest/<search>', methods=['POST'])
@functools.lru_cache(maxsize=5000)
def word_completion(search):
    search = urllib.parse.unquote(search)
    logging.debug('SUGGESTION FOR: ' + search)
    if request.method == 'POST' and len(search) > 0:
        format_query = \
            "SELECT SNIPPET(books_virtual, 0, '', '', '', 10) AS suggest FROM books_virtual WHERE title MATCH '{}*' LIMIT 1;"
        return jsonify(query_databse(search, format_query))    

@app.route('/<search>/<int:limit>', methods=['POST'])
@functools.lru_cache(maxsize=500)
def search_limit(search, limit):
    search = urllib.parse.unquote(search)
    logging.info(bcolors.color(f'SEARCH({limit}): ', bcolors.lightcyan) + search)
    if request.method == 'POST' and len(search) > 0 and limit > 0:
        search_query_limit = \
            "SELECT url FROM books_virtual WHERE books_virtual MATCH '{}' ORDER BY RANK LIMIT " + str(limit)
        return jsonify(searc_database(search, search_query_limit))


@app.route('/totalbooks', methods=['GET'])
def total_books():
    logging.info(bcolors.color('Total books query.', bcolors.lightgrey))
    if request.method == 'GET':
        return jsonify(query_databse('{}',"SELECT COUNT(*) AS count FROM books;"))

if __name__ == "__main__":
    if not (os.path.exists(SQL_DB_NAME)):
        logging.critical(bcolors.fail('Database not found. Please create database with "python3 db_update.py db_update".'))
        exit(1)
    parser = argparse.ArgumentParser(description="Local Book library server", prog="server.py")
    parser.add_argument('-d', '--debug', action="store_true", help="Start server in debug mode")
    parser.add_argument('-i', '--host', type=str, default="127.0.0.1", help="specify server ip")
    parser.add_argument('-m', '--mem', action="store_true", help="Load sqlite database in memory.")
    parser.add_argument('-p', '--port', type=int, default=9000, help="port number for server")
    parser.add_argument("-l", "--log", type=str, default='ERROR',
            choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Specify logging levels.")
    args = parser.parse_args()
    if args.debug:
        args.log = 'DEBUG'
    log_level = getattr(logging, args.log.upper(), None)
    log_format = bcolors.orange + "[%(levelname)s]" + bcolors.ENDC + ": %(message)s"
    logging.basicConfig(level=log_level, format=log_format)
    if args.mem:
        logging.info('Loading database in memory.')
        file_db = sqlite3.connect(os.path.abspath(SQL_DB_NAME), check_same_thread=False)    
        conn = sqlite3.connect('file::memory:', uri=True, check_same_thread=False)
        query = "".join(line if 'books_virtual' not in line else '' for line in file_db.iterdump())
        conn.executescript(query)
        conn.execute(BOOKS_CREATE_VIRTUAL_TABLE)
        conn.execute('INSERT INTO books_virtual SELECT title,sub_title,author,category,description, \
            year,format,url,isbn FROM books;')
        file_db.close()
    else:
        conn = sqlite3.connect(os.path.abspath(SQL_DB_NAME), check_same_thread=False)
    conn.row_factory = _dict_factory
    app.run(host=args.host, port=args.port, debug=args.debug)
