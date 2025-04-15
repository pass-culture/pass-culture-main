from pcapi.app import app
from pcapi.core.operations import models
from pcapi.repository.session_management import atomic


ID_TO_DELETE = (15, 16)


@atomic()
def delete_events() -> None:
    response_query = models.SpecialEventResponse.query.filter(models.SpecialEventResponse.eventId.in_(ID_TO_DELETE))
    models.SpecialEventAnswer.query.filter(
        models.SpecialEventAnswer.responseId.in_(response_query.with_entities(models.SpecialEventResponse.id))
    ).delete(synchronize_session=False)
    response_query.delete(synchronize_session=False)
    models.SpecialEventQuestion.query.filter(models.SpecialEventQuestion.eventId.in_(ID_TO_DELETE)).delete(
        synchronize_session=False
    )
    models.SpecialEvent.query.filter(models.SpecialEvent.id.in_(ID_TO_DELETE)).delete(synchronize_session=False)


if __name__ == "__main__":
    with app.app_context():
        delete_events()
