#!/bin/bash
mkdir venv
python3 -m venv ./venv && source ./venv/bin/activate
python3 -m pip install flask flask_cors html5lib bs4 humanfriendly ultimate-sitemap-parser lxml gunicorn
echo "activate virtul environment by: 'source ./venv/bin/activate'"
