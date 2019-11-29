from flask import Flask, jsonify, request, Response, render_template
import sqlite3
from index import SqliteConn, SQL_DB_NAME
import base64
import os
from flask_cors import CORS

app = Flask(__name__, template_folder=os.path.abspath('./build'), static_folder=os.path.abspath('./build/static'))
cors = CORS(app)

search_query = "select url from books_virtual where books_virtual match '{}' order by rank;"

# "create virtual table books_virtual using FTS5(title, sub_title, description, url)"
# "insert into books_virtual select title, sub_title, description, url from books;"
# "select url from books_virtual where books_virtual match 'c"+""+"' order by rank"

def _dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def searc_database(query, format_query):
    book_query = 'select * from books where url="{}";'
    try:
        conn = SqliteConn(SQL_DB_NAME)
        results = conn.conn.execute(format_query.format(query))
    except Exception as e:
        print(e)
        return []
    books = []
    conn.conn.row_factory = _dict_factory
    for url in results.fetchall():
        try:
            books_data = conn.conn.execute(book_query.format(url[0]))
        except Exception as e:
            print(e)
            continue
        for book in books_data.fetchall():
            try:
                book['image'] = base64.encodebytes(book['image'])
            except Exception as e:
                print('Error in image base64 conversion:', e)
            books.append(book)
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
            "select url from books_virtual where books_virtual match '{}' order by rank limit " + str(limit)
        return jsonify(searc_database(search, search_query_limit))


if __name__ == "__main__":
    app.run( host="127.0.0.28", port=9999, debug=True)
