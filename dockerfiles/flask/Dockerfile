FROM python:3

ENV PYTHONUNBUFFERED 1
RUN curl https://raw.githubusercontent.com/betagouv/pass-culture-api/master/requirements.txt > requirements.txt
RUN pip install -r requirements.txt
RUN python -m nltk.downloader punkt stopwords
WORKDIR /usr/local/bin
COPY ./start_python.sh ./
EXPOSE 5000
CMD ./start_python.sh
