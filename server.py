from flask import Flask, jsonify, request, render_template
from db_update import SqliteConn, SQL_DB_NAME
import os, functools, argparse
from flask_cors import CORS

app = Flask(__name__, template_folder=os.path.abspath('./build'), static_folder=os.path.abspath('./build/static'))
cors = CORS(app)

search_query = "SELECT url FROM books_virtual WHERE books_virtual MATCH '{}' ORDER BY RANK;"


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def query_databse(query, query_format):
    try:
        conn = SqliteConn(os.path.abspath(SQL_DB_NAME))
        conn.conn.row_factory = _dict_factory
        results = conn.conn.execute(query_format.format(query))
    except Exception as e:
        print('$0', e)
        return []
    return results.fetchall()


def searc_database(query, format_query):
    book_query = 'SELECT * FROM books WHERE url IN {};'
    try:
        conn = SqliteConn(SQL_DB_NAME)
        results = conn.conn.execute(format_query.format(query))
    except Exception as e:
        print('$1', e)
        return []
    books = []
    conn.conn.row_factory = _dict_factory
    urls = "("
    for url in results.fetchall():
        urls += '"' + str(url[0]) + '",'
    if urls[-1] == ',':
        urls = urls[0:-1]
    urls += ")"
    try:
        books = conn.conn.execute(book_query.format(urls)).fetchall()
    except Exception as e:
        print('$2', e)
    return books


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<search>', methods=['POST'])
@functools.lru_cache(maxsize=100)
def search(search):
    print("Search: ", search)
    if request.method == 'POST' and len(search) > 0 :
        return jsonify(searc_database(search, search_query))

@app.route('/suggest/<search>', methods=['POST'])
@functools.lru_cache(maxsize=5000)
def title_suggestion(search):
    if request.method == 'POST' and len(search) > 0:
        format_query = \
            "SELECT SNIPPET(books_virtual, 0, '', '', '', 10) AS suggest FROM books_virtual WHERE title MATCH '{}*' LIMIT 1;"
        return jsonify(query_databse(search, format_query))    

@app.route('/<search>/<int:limit>', methods=['POST'])
@functools.lru_cache(maxsize=500)
def search_limit(search, limit):
    print("Search: ", search)
    if request.method == 'POST' and len(search) > 0 and limit > 0:
        search_query_limit = \
            "SELECT url FROM books_virtual WHERE books_virtual MATCH '{}' ORDER BY RANK LIMIT " + str(limit)
        return jsonify(searc_database(search, search_query_limit))


if __name__ == "__main__":
    if not (os.path.exists(SQL_DB_NAME)):
        print('Database not found. Please create database with "python3 db_update.py db_update".')
        exit(1)
    parser = argparse.ArgumentParser(description="Local Book library server", prog="server.py")
    parser.add_argument('-d', '--debug', action="store_true", help="Start server in debug mode")
    parser.add_argument('-i', '--host', type=str, default="127.0.0.1", help="specify server ip")
    parser.add_argument('-p', '--port', type=int, default=9000, help="port number for server")
    args = parser.parse_args()
    app.run(host=args.host, port=args.port, debug=args.debug)
