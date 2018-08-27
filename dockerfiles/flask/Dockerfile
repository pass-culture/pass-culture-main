FROM python:3

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "/opt/services/flaskapp/src/"
WORKDIR /usr/local/bin
COPY ./start_python.sh ./
EXPOSE 5000
CMD ./start_python.sh
