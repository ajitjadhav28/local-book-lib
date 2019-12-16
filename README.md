# Website Scrapper
Collects data from allitebooks.org to search and download books faster.

## Requirements
### Run/Usage requirements
- python3, sqlite3
- Python packages: flask, flask_cors, html5lib, bs4, humanfriendly, ultimate-sitemap-parser, lxml

### Install
- Install python3 and sqlite with FTS5 support
- In system shell cd into local-book-lib and enter `python3 -m pip install -r requirements.txt`

#### Start database update : `python3 db_update.py db_update`
#### Start server after updating database by `python3 server.py` or you can use gunicorn
#### If you want to update covers locally then run `python3 db_update.py img_update` (Insreases DB size)

### Development requirements
- nodejs
- python3, sqlite3
- Python packages: flask, flask_cors, html5lib, bs4, humanfriendly, ultimate-sitemap-parser, lxml

#### Use `npm update` or `yarn` get required package(react frontend) for development.
