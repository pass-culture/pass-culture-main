FROM python:3.8-slim-buster

RUN useradd -rm -d /home/extapi -u 1000 extapi

USER extapi

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt ./requirements.txt

RUN pip install --no-cache-dir --user \
	--requirement ./requirements.txt

RUN mkdir -p /tmp/src

WORKDIR /tmp/src

COPY --chown=extapi:extapi . .

ENV PYTHONPATH=/tmp/src/external_api

ENV FLASK_APP external_api.main

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "-p", "5003"]