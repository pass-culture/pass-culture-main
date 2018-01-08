FROM python:3

ENV PYTHONUNBUFFERED 1
WORKDIR /opt/services/flaskapp/src
RUN pip install -r requirements.txt
EXPOSE 5090
CMD ["python", "app.py"]