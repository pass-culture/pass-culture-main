from models import Event


def find_by_id(event_id: str) -> Event:
    return Event.query.filter_by(id=event_id).one()
