from models import Thing


def find_by_id(id):
    return Thing.query.get(id)
