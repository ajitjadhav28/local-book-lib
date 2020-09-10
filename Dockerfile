FROM python:slim
RUN apt update && apt install -y sqlite3
# #User with home
# RUN useradd -m -s /bin/bash booklib
# USER booklib
# RUN mkdir /home/booklib/app
# VOLUME . /home/booklib/app
# WORKDIR /home/booklib/app
# #root
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt