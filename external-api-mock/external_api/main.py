from flask import Flask, request
from random import randrange
app = Flask(__name__)

@app.route('/')
def hello_geek():
    return '<h1>Hello from Flask & Docker</h2>'

@app.post('/tickets')
def create_ticket():
    print(request.form)
    return {'code': randrange(1_000_000_000, 10_000_000_000)}


if __name__ == "__main__":
    app.run(debug=True)