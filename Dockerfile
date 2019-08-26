FROM python:3

ENV PYTHONUNBUFFERED 1
WORKDIR /usr/local/bin
COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt
RUN python -m nltk.downloader punkt stopwords
EXPOSE 5000
