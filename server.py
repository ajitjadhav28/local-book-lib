from flask import Flask, jsonify, request, render_template
from db_update import SqliteConn, SQL_DB_NAME
import os
from flask_cors import CORS

app = Flask(__name__, template_folder=os.path.abspath('./build'), static_folder=os.path.abspath('./build/static'))
cors = CORS(app)

search_query = "SELECT url FROM books_virtual WHERE books_virtual MATCH '{}' ORDER BY RANK;"


def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def searc_database(query, format_query):
    book_query = 'SELECT * FROM books WHERE url IN {};'
    try:
        conn = SqliteConn(SQL_DB_NAME)
        results = conn.conn.execute(format_query.format(query))
    except Exception as e:
        print(e)
        return []
    books = []
    conn.conn.row_factory = _dict_factory
    urls = "("
    for url in results.fetchall():
        urls += '"' + str(url[0]) + '",'
    urls = urls[0:-1]+")"
    try:
        books = conn.conn.execute(book_query.format(urls)).fetchall()
    except Exception as e:
        print(e)
    return books


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<search>', methods=['POST'])
def search(search):
    print("Search: ", search)
    if request.method == 'POST' and len(search) > 0 :
        return jsonify(searc_database(search, search_query))


@app.route('/<search>/<int:limit>', methods=['POST'])
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
    app.run(host="127.0.0.28", port=9999, debug=False)
