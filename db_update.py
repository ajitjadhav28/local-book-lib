import requests, html5lib, sqlite3, logging
from bs4 import BeautifulSoup
from usp.tree import sitemap_tree_for_homepage
from multiprocessing import pool
from random import randint
from time import sleep
from user_agents import user_agents, referer
import re, humanfriendly, base64, random, string, argparse, os, json
from term_colors import bcolors
from datetime import datetime
import tqdm

BASE_URL = "http://www.allitebooks.org/sitemap.xml"
SQL_DB_NAME = "allitebooks.sql"

POSTS_CREATE_TABLE_SQL = """ CREATE TABLE IF NOT EXISTS posts(
                        id INTEGER PRIMARY KEY,
                        url TEXT NOT NULL UNIQUE,
                        last_modified TEXT NOT NULL
                        );
                    """

POSTS_INSERT_FORMAT = "INSERT INTO posts(url, last_modified) VALUES(?,?)"

DUPLICATE_BOOKS_CREATE_TABLE = """CREATE TABLE IF NOT EXISTS duplicate_books(
                                    id INTEGER PRIMARY KEY,
                                    url TEXT NOT NULL UNIQUE,
                                    book_id INTEGER NOT NULL,
                                    updated TEXT,
                                    FOREIGN KEY(book_id) REFERENCES books(id)
                                   );
                                    """

DUPLICATE_BOOKS_INSERT_FORMAT = """INSERT INTO duplicate_books(url, book_id, updated)
                                    VALUES("{url}", "{book_id}", "{updated}");"""

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
                             "category, description, year, format, url, isbn); "

BOOKS_VIRT_INSRT_FRMT = """INSERT INTO books_virtual(title,sub_title,author,category,description,year,format,url,isbn)
VALUES("{title}","{sub_title}","{author}","{category}","{description}","{year}","{format}","{url}", "{isbn}") """


class SqliteConn:
    def __init__(self, file_name: str):
        self._db_name = file_name
        self._connection = None
        try:
            self._connection = sqlite3.connect(self._db_name)
        except sqlite3.Error as e:
            logging.critical(bcolors.fail(e))
            self.__del__()

    @property
    def conn(self):
        if self._connection:
            return self._connection

    def get_db_name(self):
        if self._db_name:
            return self._db_name

    def __del__(self):
        logging.info("Closing database connection.")
        if self._connection:
            self._connection.close()


def _iso8601_time_now() -> str:
    return datetime.now().replace(microsecond=0).isoformat()


def _replace_double_quotes(data: str):
    return data.strip().replace('"', "'")


def _extract_data(data: list, index: int, url: str, atr: str) -> str:
    tmp = ""
    try:
        tmp = _replace_double_quotes(str(data[index]))
    except Exception as e:
        logging.debug(e)
        logging.warning("Attribute '" + atr + "' not found for : " + bcolors.warn(url))
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


def __extract_loc(url):
    br = requests.get(url, headers=_get_random_header())
    bsoup = BeautifulSoup(br.content, "lxml")
    bkurls = bsoup.findAll('loc')
    return [burl.text for burl in bkurls]


def _fetch_only_sitemap(db: SqliteConn, procs: int = 6):
    r = requests.get(BASE_URL, headers=_get_random_header())
    interested_posts = re.compile('^http?://www.allitebooks.org/post-sitemap[0-9]+.xml$')
    soup = BeautifulSoup(r.content, "lxml")
    all_url = soup.find_all('loc')
    all_posts = []
    for url in all_url:
        if interested_posts.match(url.text):
            all_posts.append(url.text)
    all_books = []
    try:
        SitemapWorker = pool.Pool(processes=procs)
        work = SitemapWorker.imap_unordered(__extract_loc, all_posts)
        for subwork in work:
            all_books.extend(subwork)
    except Exception as e:
        logging.debug(e)
        logging.info("Trying single thread")
        for post in all_posts:
            all_books.extend(__extract_loc(post))

    db_books = db.conn.execute("SELECT url FROM books;").fetchall()
    duplicate_books = db.conn.execute("SELECT url from duplicate_books;").fetchall()
    duplicate_books = [db[0] for db in duplicate_books]
    logging.debug(f'Duplicate books in database: {len(duplicate_books)}')
    logging.debug(f'Books found in sitemap: {len(all_books)}')
    logging.debug(f'Total books in database: {len(db_books)}')
    db_books = [book[0] for book in db_books]
    db_books.extend(duplicate_books)
    new_books = set(all_books) - set(db_books)
    logging.debug(f'New books found: {len(new_books)}')
    # for book in all_books:
    #     cur = db.conn.execute("SELECT COUNT(*) from books where url='{}';".format(book))
    #     dt = cur.fetchone()
    #     if dt[0] == 0:
    #         new_books.append(book)
    return list(new_books)


def get_book_details(url: str):
    r = None
    delay = randint(0, 2) * random.random()
    sleep(delay)
    try:
        r = requests.get(url, headers=_get_random_header(), timeout=(5, 15))
    except Exception as e:
        logging.debug(e)
        logging.warning("Request failed for: " + bcolors.warn(url))
        return {'title': None, 'url': url}
    soup = BeautifulSoup(r.content, 'html5lib')
    book_details = {}

    try:
        book_details['title'] = str(soup.find('h1', attrs={'class': 'single-title'}).text).strip().replace('"', "'")
    except Exception as e:
        logging.debug(e)
        logging.warning("Title for book not found: " + bcolors.warn(url))
        logging.warning("Ignoring this url.")
        return {'title': None, 'url': url}

    try:
        book_details['sub_title'] = str(soup.find('header', attrs={'class': 'entry-header'}).h4.text).strip().replace(
            '"', "'")
    except Exception as e:
        logging.debug(e)
        logging.warning("Subtitle not found: " + bcolors.warn(url))
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
    new_lines = re.compile('\n\n+')
    tabs = re.compile('\t\t+')
    try:
        book_details['description'] = str(desc_div.text).strip().replace(str(desc_div.h3.text), "")
        book_details['description'] = new_lines.sub('\n', book_details['description'])
        book_details['description'] = tabs.sub('\t', book_details['description'])
        if book_details['description'][0] == '\n':
            book_details['description'] = book_details['description'][1:]
        book_details['description'] = _replace_double_quotes(book_details['description'])
    except Exception as e:
        logging.debug(e)
        logging.warning("Description not found for book: " + book_details['title'])
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
                logging.debug(e)

        elif dt.a['href'].find('.epub') > 0:
            book_details['epub_url'] = dt.a['href']
            try:
                book_details['epub_size'] = humanfriendly.parse_size(dt.a.span.text.strip('()'))
            except Exception as e:
                logging.debug(e)
        else:
            book_details['other_url'] = dt.a['href']
            try:
                book_details['other_size'] = humanfriendly.parse_size(dt.a.span.text.strip('()'))
            except Exception as e:
                logging.debug(e)
    try:
        book_details['image_url'] = \
            str(soup.find('img', attrs={'class': 'attachment-post-thumbnail wp-post-image'})['src']).strip()
    except Exception as e:
        logging.debug(e)
        book_details['image_url'] = None

    return book_details


def _insert_post(db: SqliteConn, url: str, last_modified):
    try:
        db.conn.execute(POSTS_INSERT_FORMAT, (url, last_modified))
    except Exception as e:
        logging.error(e)
        return False
    db.conn.commit()
    return True


def insert_posts(db: SqliteConn, data: set):
    for d in data:
        url, last_mod = str(d).split("#$#")
        _insert_post(db, url, last_mod)
    db.conn.commit()


def _scrapping_website(db: SqliteConn):
    all_book_pages = set([])
    all_post_pages = set([])
    tree = sitemap_tree_for_homepage(BASE_URL)
    url_check = re.compile("^http?://.*/.*/$")
    for page in tree.all_pages():
        if page.url.find("/author/") < 0 \
                and page.url.find("/tagtagtag/") < 0 \
                and page.url.find("/?") < 0 \
                and url_check.match(page.url) is not None:
            cur = db.conn.execute("SELECT COUNT(*) from posts where url='{}';".format(page.url))
            dt = cur.fetchone()
            if dt[0] == 0:
                all_book_pages.add(str(page.url))
                all_post_pages.add(str(page.url) + '#$#' + str(page.last_modified))
    return (all_book_pages, all_post_pages)


def _get_book_id(isbn: str, db: SqliteConn) -> int:
    try:
        r = db.conn.execute(f'SELECT id from books where isbn="{isbn}";').fetchone()
    except Exception as e:
        logging.debug("Exception while fetching id of book")
        logging.debug(e)
        return -1
    if r is None:
        return -1
    return r[0]


def backup(scraping_sitemap: bool = True, procs: int = 10):
    db = SqliteConn(SQL_DB_NAME)
    db.conn.execute(BOOKS_CREATE_TABLE)
    db.conn.execute(POSTS_CREATE_TABLE_SQL)
    db.conn.execute(BOOKS_CREATE_VIRTUAL_TABLE)
    db.conn.execute(DUPLICATE_BOOKS_CREATE_TABLE)
    db.conn.commit()
    all_post_pages = []
    all_book_pages = []
    if scraping_sitemap:
        all_book_pages = all_post_pages = _fetch_only_sitemap(db, procs)
    else:
        all_book_pages, all_post_pages = _scrapping_website(db)
        insert_posts(db, all_post_pages)
    print(bcolors.blue("Found " + str(len(all_book_pages)) + " book pages."))
    sleep(0.1)
    PBAR = tqdm.tqdm(total=len(all_book_pages), unit=" book", desc=bcolors.color("checking books", bcolors.lightgreen), ascii=True)
    try:
        BookWorker = pool.Pool(processes=procs)
        book_data = BookWorker.imap_unordered(get_book_details, all_book_pages)
        BookWorker.close()
    except Exception as e:
        logging.debug(e)
        logging.info("Trying with single thread")
        book_data = []
        all_book_pages = tuple(all_book_pages)
        for book_page in all_book_pages:
            PBAR.update(1)
            book_data.append(get_book_details(book_page))
    else:
        a, b = 0, book_data._index + 1
        t = len(all_book_pages)
        while b <= t:
            PBAR.update(b-a)
            a, b = b, book_data._index + 1
    
    PBAR.close()

    books_updated = []
    book_data = filter(lambda b: b['title'] is not None, book_data)
    book_data = tuple(book_data)
    t = len(book_data)
    duplicate_books = []
    PBAR = tqdm.tqdm(total=t, desc=bcolors.blue("updating database"), unit=" book", ascii=True)
    for book in book_data:
        try:
            db.conn.execute('BEGIN')
            db.conn.execute(BOOKS_INSERT_FORMAT.format(**book))
            db.conn.execute(BOOKS_VIRT_INSRT_FRMT.format(**book))
        except sqlite3.IntegrityError as e:
            logging.debug(bcolors.color('[IntegrityError] ', bcolors.yellow) + str(e))
            db.conn.execute('ROLLBACK')
            logging.warning(bcolors.color('Book already exists: ', bcolors.orange) + book['title'])
            logging.info("Adding this book url to duplicates table.")
            duplicate_books.append({
                'url': book['url'],
                'book_id': _get_book_id(book['isbn'], db),
                'updated': _iso8601_time_now()
            })
            continue
        except Exception as e:
            logging.warning(bcolors.color('[Other] ', bcolors.yellow) + str(e) + " url=" + bcolors.warn(book['url']))
            logging.debug('Book data: ')
            logging.debug(str(book))
            db.conn.execute('ROLLBACK')
            continue
        books_updated.append(book['title'])
        db.conn.commit()
        PBAR.update(1)
    PBAR.close()
    if len(duplicate_books) > 0:
        print(bcolors.color(f'Duplicate books found: {len(duplicate_books)}.', color=bcolors.purple))
    
    if len(books_updated) > 0:
        print(bcolors.green("Updated database with " + str(len(books_updated)) + " new books."))
    elif len(books_updated) == 0:
        print(bcolors.color('No new books found.', bcolors.yellow))

    if len(books_updated) < 50:
        for i, book in enumerate(books_updated):
            print(bcolors.color('\t{}) {}'.format(i + 1, book), bcolors.lightgreen))

    for book in duplicate_books:
        try:
            db.conn.execute(DUPLICATE_BOOKS_INSERT_FORMAT.format(**book))
        except Exception as e:
            logging.debug("Error while adding duplicate books.")
            logging.debug(e)
            continue
        db.conn.commit()


def _update_image(db, image_url: str):
    _base64_string = lambda raw_byte: base64.encodebytes(raw_byte).decode('utf-8')
    try:
        image_request = requests.get(image_url, headers=_get_random_header(), timeout=(5, 15))
        db.execute('BEGIN')
        db.execute('UPDATE books SET image=? WHERE image_url=?', (_base64_string(image_request.content), image_url))
    except Exception as e:
        logging.error("ERROR while updating image for: ", image_url)
        db.execute('ROLLBACK')
        return False
    db.commit()
    logging.info("Image Updated: ", image_url)
    return True


def update_images():
    db = sqlite3.connect(SQL_DB_NAME)
    images = None
    try:
        images = db.execute('SELECT image_url FROM books WHERE image_url IS NOT "None" and image isnull;')
    except Exception as e:
        logging.debug(e)
        logging.error("Can't fetch image url data from database.")
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
                logging.error('Error while updating new book.' + url[0])
                unique_isbn = re.compile('^UNIQUE.*books.isbn$')
                logging.debug(e)
                db.execute("ROLLBACK")
                if unique_isbn.match(str(e)) is not None:
                    logging.info('Removing duplicate book')
                    db.execute('DELETE FROM books WHERE url="{}"'.format(url[0]))
                    db.commit()
                continue
            db.commit()
            _update_image(db, url[0])
    db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=bcolors.header("This program collect data from website 'allitebooks.org'. It creates "
                                   "local copy to search and download books faster. If you want "
                                   "lightweight database then don't update images in database. For "
                                   "first run it may take good amount of time be patient."
                                   )
    )
    parser.add_argument("action", help="Specify action: db_update, img_update")
    parser.add_argument("-w", "--website", action="store_true",
                        help="Scraps whole website sitemap instead of just book links from sitemap. It may take extra time.")
    parser.add_argument("-l", "--log", type=str, default='ERROR',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], help="Specify logging levels.")
    parser.add_argument('-j', '--jobs', default=10, type=int, help="No of parallel jobs of worker.")

    args = parser.parse_args()
    log_level = getattr(logging, args.log.upper(), None)
    log_format = bcolors.FAIL + "[%(levelname)s]" + bcolors.ENDC + ": %(message)s"
    logging.basicConfig(level=log_level, format=log_format)
    if args.action == 'db_update':
        print(bcolors.header('Updating database. This may take time.'))
        print(bcolors.header('Starting website scraping..'))
        backup(not args.website, args.jobs)
    elif args.action == 'img_update':
        if not os.path.exists(SQL_DB_NAME):
            logging.critical(bcolors.fail("Database does not exists. Please create database first using 'db_update' "
                                          "argument."))
            exit(1)
        else:
            print(bcolors.header('Downloading images into database.'))
            update_images()
