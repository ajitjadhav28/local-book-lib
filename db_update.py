import requests, html5lib, sqlite3
from bs4 import BeautifulSoup
from usp.tree import sitemap_tree_for_homepage
from multiprocessing import pool
from random import randint
from time import sleep
from user_agents import user_agents, referer
import re, humanfriendly, base64, random, string, argparse, os, json

BASE_URL = "http://www.allitebooks.org/sitemap.xml"
SQL_DB_NAME = "allitebooks.sql"

POSTS_CREATE_TABLE_SQL = """ CREATE TABLE IF NOT EXISTS posts(
                        id INTEGER PRIMARY KEY,
                        url TEXT NOT NULL UNIQUE,
                        last_modified TEXT NOT NULL
                        );
                    """

POSTS_INSERT_FORMAT = "INSERT INTO posts(url, last_modified) VALUES(?,?)"

BOOKS_CREATE_TABLE = """ CREATE TABLE IF NOT EXISTS books(
                        id INTEGER PRIMARY KEY,
                        title TEXT,
                        sub_title TEXT,
                        author TEXT,
                        category TEXT,
                        description TEXT,
                        isbn TEXT NOT NULL UNIQUE,
                        year TEXT,
                        pages INTEGER,
                        language TEXT,
                        format TEXT,
                        url TEXT NOT NULL UNIQUE,
                        epub_url TEXT,
                        epub_size INTEGER,
                        pdf_url TEXT,
                        pdf_size INTEGER,
                        other_url TEXT,
                        other_size INTEGER,
                        image_url TEXT,
                        image BLOB
                        );
                    """

BOOKS_INSERT_FORMAT = """INSERT INTO books(title,sub_title,author,category,description,isbn,year,pages,language,
format,url, epub_url,epub_size,pdf_url,pdf_size,other_url,other_size,image_url) VALUES("{title}","{sub_title}",
"{author}","{category}","{description}", "{isbn}","{year}","{pages}","{language}","{format}","{url}","{epub_url}",
"{epub_size}","{pdf_url}","{pdf_size}", "{other_url}","{other_size}","{image_url}") """

BOOKS_CREATE_VIRTUAL_TABLE = "CREATE VIRTUAL TABLE IF NOT EXISTS books_virtual USING FTS5(title, sub_title, author, " \
                             "category, description, year, format, url); "

BOOKS_VIRT_INSRT_FRMT = """INSERT INTO books_virtual(title,sub_title,author,category,description,year,format,url)
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
            sz = dt.a.span.text.strip('()')
            if sz.find(',') > -1:
                sz = sz.replace(',', '.')
            try:
                book_details['pdf_size'] = humanfriendly.parse_size(sz)
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
        db.conn.execute('BEGIN')
        db.conn.execute(POSTS_INSERT_FORMAT, (url, last_modified))
    except Exception as e:
        print(e, "$2")
        db.conn.execute('ROLLBACK')
        return False
    db.conn.commit()
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
    db.conn.execute(BOOKS_CREATE_VIRTUAL_TABLE)
    db.conn.commit()
    all_book_pages = set([])
    all_post_pages = set([])
    tree = sitemap_tree_for_homepage("http://www.allitebooks.org/sitemap.xml")
    url_check = re.compile("http?://.*/.*/.*/.*")
    for page in tree.all_pages():
        if page.url.find("/author/") < 0 \
                and page.url.find("/tagtagtag/") < 0 \
                and page.url.find("/?") < 0 \
                and url_check.match(page.url) is None:
            cur = db.conn.execute("SELECT COUNT(*) from posts where url='{}';".format(page.url))
            dt = cur.fetchone()
            if dt[0] == 0:
                all_book_pages.add(str(page.url))
                all_post_pages.add(str(page.url) + '#$#' + str(page.last_modified))

    insert_posts(db, all_post_pages)

    BookWorker = pool.Pool(processes=10)
    book_data = BookWorker.map(get_book_details, list(all_book_pages))

    # try:
    #     with open("books.json", 'r+') as file:
    #         old_data = []
    #         try:
    #             old_data = json.loads(file.read())
    #         except Exception as e:
    #             print(e)
    #         old_data.extend(book_data)
    #         file.write(json.dumps(old_data))
    # except Exception as e:
    #     print("Error in saving json data: ", e)

    # try:
    #     with open("books.json", 'r') as file:
    #         book_data = json.loads(file.read())
    # except Exception as e:
    #     print(e)

    books_updated = 0
    total_books = len(book_data)
    print("Found ", total_books, " books.")
    print("Updating new books.")
    for book in book_data:
        if book is not None:
            try:
                print('Trying book: ', book['url'])
                db.conn.execute('BEGIN')
                db.conn.execute(BOOKS_INSERT_FORMAT.format(**book))
                db.conn.execute(BOOKS_VIRT_INSRT_FRMT.format(**book))
            except Exception as e:
                print(e, ", url=", book['url'])
                db.conn.execute('ROLLBACK')
                continue
            books_updated += 1
            db.conn.commit()
        sleep(0.001)
    print("Updated database with ", books_updated, " new books.")


def _update_image(db, image_url: str):
    _base64_string = lambda raw_byte : base64.encodebytes(raw_byte).decode('utf-8')
    try:
        image_request = requests.get(image_url, headers=_get_random_header(), timeout=(5, 15))
        db.execute('BEGIN')
        db.execute('UPDATE books SET image=? WHERE image_url=?', (_base64_string(image_request.content), image_url))
    except Exception as e:
        print("ERROR while updating image for: ", image_url)
        db.execute('ROLLBACK')
        return False
    db.commit()
    print("Image Updated: ", image_url)
    return True


def update_images():
    db = sqlite3.connect(SQL_DB_NAME)
    images = None
    try:
        images = db.execute('SELECT image_url FROM books WHERE image_url IS NOT "None" and image isnull;')
    except Exception as e:
        print("Can't fetch image url data from database.", e)
        return
    i = 1
    for image in images.fetchall():
        if _update_image(db, image[0]):
            i += 1
    print("Total images updated: ", i)
    db.close()


def _random_str(n: int):
    r = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=n))
    return r


def _update_null_url_books():
    check_updated = lambda bk: bk['pdf_url'] is not None \
                               or bk['epub_url'] is not None \
                               or bk['other_url'] is not None

    db = sqlite3.connect(SQL_DB_NAME)
    urls = db.execute("SELECT url FROM books WHERE pdf_url ISNULL AND epub_url ISNULL AND other_url ISNULL;")
    for url in urls.fetchall():
        new_book = get_book_details(url[0])
        if check_updated(new_book):
            if new_book['isbn'] is None:
                new_book['isbn'] = _random_str(10)
            try:
                print("Updating book", new_book['url'])
                db.execute('BEGIN')
                db.execute('DELETE FROM books WHERE url="{}"'.format(url[0]))
                db.execute('DELETE FROM books_virtual WHERE url="{}"'.format(url[0]))
                db.execute(BOOKS_INSERT_FORMAT.format(**new_book))
                db.execute(BOOKS_VIRT_INSRT_FRMT.format(**new_book))
            except Exception as e:
                print('Error while updating new book.', url[0])
                unique_isbn = re.compile('^UNIQUE.*books.isbn$')
                print(e)
                db.execute("ROLLBACK")
                if unique_isbn.match(str(e)) is not None:
                    print('Removing duplicate book')
                    db.execute('DELETE FROM books WHERE url="{}"'.format(url[0]))
                    db.commit()
                continue
            db.commit()
            _update_image(db, url[0])
    db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This program collect data from website 'allitebooks.org'. It creates "
                                                 "local copy to search and download books faster. If you want "
                                                 "lightweight database then don't update images in database. For "
                                                 "first run it may take good amount of time be patient.")
    parser.add_argument("action", help="Specify action: db_update, img_update")
    args = parser.parse_args()
    if args.action == 'db_update':
        print('Updating database. This may take time.')
        print('Starting website scraping..')
        backup()
    elif args.action == 'img_update':
        if not os.path.exists(SQL_DB_NAME):
            print("Database does not exists. Please create database first using 'db_update' argument.")
            exit(1)
        else:
            print('Downloading images into database.')
            update_images()
