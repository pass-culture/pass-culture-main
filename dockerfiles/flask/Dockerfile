FROM python:3

ENV PYTHONUNBUFFERED 1
WORKDIR /usr/local/bin
COPY ./start_python.sh ./
RUN ls
EXPOSE 5000
CMD ./start_python.sh