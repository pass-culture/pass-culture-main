FROM python:3.7.6-slim

ENV PYTHONUNBUFFERED 1
WORKDIR /usr/local/bin
RUN apt update && apt-get -y install gcc
COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt
RUN python -m nltk.downloader punkt stopwords
EXPOSE 5000
