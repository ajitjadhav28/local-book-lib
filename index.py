import requests
from bs4 import BeautifulSoup
import html5lib
from usp.tree import sitemap_tree_for_homepage
import sqlite3
from multiprocessing import pool
import json
from random import randint
from time import sleep
from user_agents import user_agents, referer
import re
import humanfriendly

BASE_URL = "http://www.allitebooks.org/sitemap.xml"
SQL_DB_NAME = "allitebooks.sql"

POSTS_CREATE_TABLE_SQL = """ CREATE TABLE IF NOT EXISTS posts(
                        id integer PRIMARY KEY,
                        url text NOT NULL UNIQUE,
                        last_modified text NOT NULL
                        );
                    """

POSTS_INSERT_FORMAT = "INSERT INTO posts(url, last_modified) VALUES(?,?)"

BOOKS_CREATE_TABLE = """ CREATE TABLE IF NOT EXISTS books(
                        id integer PRIMARY KEY,
                        title text,
                        sub_title text,
                        author text,
                        category text,
                        description text,
                        isbn text UNIQUE,
                        year text,
                        pages integer,
                        language text,
                        format text,
                        url text NOT NULL UNIQUE,
                        epub_url text,
                        epub_size integer,
                        pdf_url text,
                        pdf_size integer,
                        other_url text,
                        other_size integer,
                        image_url text,
                        image BLOB
                        );
                    """

BOOKS_INSERT_FORMAT = """INSERT INTO books(title,sub_title,author,category,description,isbn,year,pages,language,format,url,
epub_url,epub_size,pdf_url,pdf_size,other_url,other_size,image_url) VALUES("{title}","{sub_title}","{author}","{category}","{description}",
"{isbn}","{year}","{pages}","{language}","{format}","{url}","{epub_url}","{epub_size}","{pdf_url}","{pdf_size}",
"{other_url}","{other_size}","{image_url}") """

BOOKS_VIRT_INSRT_FRMT = """INSERT INTO books(title,sub_title,author,category,description,year,format,url)
VALUES("{title}","{sub_title}","{author}","{category}","{description}","{year}","{format}","{url}") """


class SqliteConn:
    def __init__(self, file_name: str):
        self._db_name = file_name
        self._connection = None
        try:
            self._connection = sqlite3.connect(self._db_name)
        except sqlite3.Error as e:
            print(e)
            self.__del__()

    @property
    def conn(self):
        if self._connection:
            return self._connection

    def get_db_name(self):
        if self._db_name:
            return self._db_name

    def __del__(self):
        print("Closing database connection.")
        if self._connection:
            self._connection.close()


def _extract_data(data: list, index: int, url: str, atr: str) -> str:
    tmp = ""
    try:
        tmp = str(data[index]).strip()
    except Exception as e:
        print("Exception: ", e)
        print("Attribute '", atr, "' not found for : ", url)
        return None
    return tmp


def _get_random_header():
    headers = {
        'user-agent': user_agents[randint(0, len(user_agents) - 1)],
        'referrer': referer[randint(0, len(referer) - 1)],
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-US,en;q=0.9',
        'Pragma': 'no-cache',
    }
    return headers


def get_book_details(url: str):

    r = None
    delay = randint(0, 2)
    sleep(delay)
    try:
        r = requests.get(url, headers=_get_random_header(), timeout=(5, 15))
    except Exception as e:
        print("Exception: ", e)
        print("Request failed for: ", url)
        return None
    soup = BeautifulSoup(r.content, 'html5lib')
    book_details = {}

    try:
        book_details['title'] = str(soup.find('h1', attrs={'class': 'single-title'}).text).strip()
    except Exception as e:
        print("Exception: ", e)
        print("Title for book not found: ", url)
        return None

    try:
        book_details['sub_title'] = str(soup.find('header', attrs={'class': 'entry-header'}).h4.text).strip()
    except Exception as e:
        print("Exception: ", e)
        print("Subtitle not found: ", url)
        book_details['sub_title'] = None

    table = soup.find('div', attrs={'class': 'book-detail'})
    dd = table.findAll('dd')
    dd_data = []
    for d in dd:
        if d.a:
            dd_data.append(d.a.contents[0])
        else:
            dd_data.append(d.contents[0])
    book_details['author'] = _extract_data(dd_data, 0, url, 'author')
    book_details['isbn'] = _extract_data(dd_data, 1, url, 'isbn')
    book_details['year'] = _extract_data(dd_data, 2, url, 'year')
    book_details['pages'] = _extract_data(dd_data, 3, url, 'pages')
    book_details['language'] = _extract_data(dd_data, 4, url, 'language')
    book_details['format'] = _extract_data(dd_data, 6, url, 'format')
    book_details['category'] = _extract_data(dd_data, 7, url, 'category')
    book_details['url'] = url
    desc_div = soup.find('div', attrs={'class': 'entry-content'})
    try:
        if desc_div.p:
            book_details['description'] = str(desc_div.p.text).strip()
        elif desc_div.div:
            book_details['description'] = str(desc_div.div.text).strip()
        elif desc_div.ul:
            book_details['description'] = str(desc_div.ul.text).strip()
        else:
            book_details['description'] = str(desc_div.text).strip().replace(str(desc_div.h3.text), "")
    except Exception as e:
        print("Exception: ", e)
        print("Description not found for book: ", book_details['title'])
        book_details['description'] = None
    down_data = soup.findAll('span', attrs={'class': 'download-links'})
    book_details['pdf_url'] = None
    book_details['pdf_size'] = 0
    book_details['epub_url'] = None
    book_details['epub_size'] = 0
    book_details['other_url'] = None
    book_details['other_size'] = 0
    for dt in down_data:
        if dt.a['href'].find('.pdf') > 0:
            book_details['pdf_url'] = dt.a['href']
            try:
                book_details['pdf_size'] = humanfriendly.parse_size(dt.a.span.text.strip('()'))
            except Exception as e:
                print(e)

        elif dt.a['href'].find('.epub') > 0:
            book_details['epub_url'] = dt.a['href']
            try:
                book_details['epub_size'] = humanfriendly.parse_size(dt.a.span.text.strip('()'))
            except Exception as e:
                print(e)
        else:
            book_details['other_url'] = dt.a['href']
            try:
                book_details['other_size'] = humanfriendly.parse_size(dt.a.span.text.strip('()'))
            except Exception as e:
                print(e)
    try:
        book_details['image_url'] = \
            str(soup.find('img', attrs={'class': 'attachment-post-thumbnail wp-post-image'})['src']).strip()
    except Exception as e:
        print('Thumbnail Exception: ', e)
        book_details['image_url'] = None

    return book_details


def _insert_post(db: SqliteConn, url: str, last_modified):
    try:
        db.conn.execute(POSTS_INSERT_FORMAT, (url, last_modified))
    except Exception as e:
        print(e, "$2")
        return False
    return True


def insert_posts(db: SqliteConn, data: set):
    for d in data:
        url, last_mod = str(d).split("#$#")
        _insert_post(db, url, last_mod)
    db.conn.commit()


def backup():
    db = SqliteConn(SQL_DB_NAME)
    db.conn.execute(BOOKS_CREATE_TABLE)
    db.conn.execute(POSTS_CREATE_TABLE_SQL)
    all_book_pages = set([])
    all_post_pages = set([])
    tree = sitemap_tree_for_homepage("http://www.allitebooks.org/sitemap.xml")
    url_check = re.compile("http?://.*/.*/.*/.*")
    for page in tree.all_pages():
        if page.url.find("/author/") < 0 \
                and page.url.find("/tagtagtag/") < 0 \
                and page.url.find("/?") < 0\
                and url_check.match(page.url) is None:
            cur = db.conn.execute("SELECT COUNT(*) from posts where url='{}';".format(page.url))
            dt = cur.fetchone()
            if dt[0] == 0:
                all_book_pages.add(str(page.url))
                all_post_pages.add(str(page.url) + '#$#' + str(page.last_modified))

    insert_posts(db, all_post_pages)

    # cur = db.conn.execute("SELECT url from posts;")
    # all_book_pages = [url[0] for url in list(cur.fetchall())]

    BookWorker = pool.Pool(processes=10)
    book_data = BookWorker.map(get_book_details, list(all_book_pages))

    try:
        with open("books.json", 'r+') as file:
            old_data = []
            try:
                old_data = json.loads(file.read())
            except Exception as e:
                print(e)
            old_data.extend(book_data)
            file.write(json.dumps(old_data))
    except Exception as e:
        print("Error in saving json data: ", e)

    # try:
    #     with open("books.json", 'r') as file:
    #         book_data = json.loads(file.read())
    # except Exception as e:
    #     print(e)

    for book in book_data:
        if book is not None:
            try:
                print('Trying book: ', book['url'])
                db.conn.execute(BOOKS_INSERT_FORMAT.format(**book))
            except Exception as e:
                print(e, ", url=", book['url'])
            try:
                db.conn.execute(BOOKS_VIRT_INSRT_FRMT.format(**book))
            except Exception as e:
                print('Virtual table update error', e, book['url'])
            db.conn.commit()
        sleep(0.001)


def _update_images():
    db = sqlite3.connect(SQL_DB_NAME)
    images = None
    try:
        images = db.execute('SELECT image_url FROM books WHERE image_url IS NOT "None" and image isnull;')
    except Exception as e:
        print("Can't fetch image url data from database.")
        print(e)
        return

    for image in images.fetchall():
        try:
            image_request = requests.get(image[0], headers=_get_random_header(), timeout=(5, 15))
            db.execute('UPDATE books SET image=? WHERE image_url=?', (image_request.content, image[0]))
        except Exception as e:
            print("ERROR while updating image for: ", image)
            continue
        print("Image updated: ", image[0])
        db.commit()
    db.close()


def _format_size_oldjson():
    """Convert old human readable size to bytes of json"""

    def update_books(book_data= []):

        db_conection = SqliteConn('allitebooks.db')
        for book in book_data:
            if book is not None:
                try:
                    print('Trying book: ', book['url'])
                    db_conection.conn.execute(BOOKS_INSERT_FORMAT.format(**book))
                except Exception as e:
                    print(e, ", url=", book['url'])
                db_conection.conn.commit()
            sleep(0.001)

    new = []
    with open("books.json", 'r') as file:
        old = json.loads(file.read())
        for book in old:
            if book is not None:
                try:
                    book['pdf_size'] = humanfriendly.parse_size(book['pdf_size'])
                except Exception as e:
                    book['pdf_size'] = 0
                try:
                    book['epub_size'] = humanfriendly.parse_size(book['epub_size'])
                except Exception as e:
                    book['epub_size'] = 0
                try:
                    book['other_size'] = humanfriendly.parse_size(book['other_size'])
                except Exception as e:
                    book['other_size'] = 0
                new.append(book)
    with open("books.json", 'w') as file:
        file.write(json.dumps(new))

    update_books(new)


if __name__ == "__main__":
    backup()