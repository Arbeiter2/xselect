FROM python:3.8-slim-buster

RUN apt-get update --fix-missing
COPY google-chrome-stable_current_amd64.deb /tmp/google-chrome-stable_current_amd64.deb
RUN apt-get install -y /tmp/google-chrome-stable_current_amd64.deb
WORKDIR /app
COPY requirements.txt requirements.txt
RUN python3 -m pip install --upgrade pip
RUN pip3 install -r requirements.txt
#RUN groupadd -g 1000 delano
#RUN useradd --no-create-home -r -u 1000 -g 1000 delano
#USER delano
COPY scraper.py .
COPY onlyfinder.py .
COPY onlyfinder.json .
# map home dir to /mnt/chronos
ENTRYPOINT [ "python3", "onlyfinder.py"]
ENV [0, muscle]
