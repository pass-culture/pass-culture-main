"""events"""
from flask import current_app as app, jsonify

#event_types = [et.name for et in list(app.model.EventType)]
event_types = [
    {
        "value": "",
        "label": "(Aucun)"
    },
    {
        "value": "ComedyEvent",
        "label": "Show"
    },
    {
        "value": "DanceEvent",
        "label": "Danse"
    },
    {
        "value": "Festival",
        "label": "Festival"
    },
    {
        "value": "LiteraryEvent",
        "label": "Litérature"
    },
    {
        "value": 'MusicEvent',
        "label": "Musique"
    },
    {
        "value": 'ScreeningEvent',
        "label": "Cinéma"
    },
    {
        "value": 'TheaterEvent',
        "label": "Théâtre"
    }
]

@app.route('/eventTypes', methods=['GET'])
def list_event_types():
    return jsonify(event_types), 200
