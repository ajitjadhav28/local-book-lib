# Website Scrapper
Collects data from allitebooks.org to search and download books faster.

## Screenshot
![Screenshot of app on firefox](https://github.com/ajitjadhav28/local-book-lib/blob/master/screenshot.png)

## Requirements
### Run/Usage requirements
- python3, sqlite3
- pathon packages from requirements.txt 

### Install
- Install python3 and sqlite with FTS5 support
- In system shell cd into local-book-lib and enter `python3 -m pip install -r requirements.txt`

#### Start database update : `python3 db_update.py db_update`
#### Start server after updating database by `python3 server.py` or you can use gunicorn
#### If you want to update covers locally then run `python3 db_update.py img_update` (Insreases DB size)

### Development requirements
- nodejs
- python3, sqlite3
- python packages from requirements.txt

#### Use `npm update` or `yarn` get required package(react frontend) for development.
