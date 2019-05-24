FROM python:3

ENV PYTHONUNBUFFERED 1
WORKDIR /usr/local/bin
RUN pip install -r requirements.txt
COPY ./start_python.sh ./
EXPOSE 5000
CMD ./start_python.sh
