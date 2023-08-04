from flask import Flask, request
from random import randrange
app = Flask(__name__)

@app.route('/')
def hello_geek():
    return '<h1>Hello from Flask & Docker</h2>'

@app.post('/tickets/create')
def create_ticket():
    print(request.form)
    return {'code': randrange(1_000_000_000, 10_000_000_000)}, 201

@app.get('/tickets/<int:ticket_id>')
def get_ticket(ticket_id):
    return {'code': ticket_id, 'status': 'open'}, 200

@app.post('/tickets/<int:ticket_id>/delete')
def delete_ticket(ticket_id):
    return ('',204)


if __name__ == "__main__":
    app.run(debug=True)