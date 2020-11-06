FROM python:slim
RUN apt update
RUN apt install -y sqlite3
RUN apt install -y gcc make python3-lxml 
# #User with home
# RUN useradd -m -s /bin/bash booklib
# USER booklib
# RUN mkdir /home/booklib/app
# VOLUME . /home/booklib/app
# WORKDIR /home/booklib/app
# #root
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt