import datetime
import logging

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.operations import factories as operations_factories


logger = logging.getLogger(__name__)


def create_special_events() -> None:
    logger.info("create_special_events")

    _create_special_event_with_date()
    _create_special_event_with_venue()

    logger.info("created special events")


def _create_special_event_with_date() -> None:
    event_date = datetime.date.today() + datetime.timedelta(days=15)
    event = operations_factories.SpecialEventFactory(
        externalId="fake00001", title="Jeu concours : gagne une place de concert", eventDate=event_date
    )
    operations_factories.SpecialEventQuestionFactory(
        event=event,
        externalId="00001-abcde-00001",
        title=f"Es-tu disponible le {event_date.strftime('%d/%m/%Y')} à 20h30 ?",
    )
    operations_factories.SpecialEventQuestionFactory(
        event=event,
        externalId="00001-abcde-00002",
        title="Où habites-tu ?",
    )
    operations_factories.SpecialEventQuestionFactory(
        event=event,
        externalId="00001-abcde-00003",
        title="Explique-nous pourquoi tu souhaites être sélectionné !",
    )


def _create_special_event_with_venue() -> None:
    venue = offerers_factories.VenueFactory(
        managingOfferer__name="Structure associée à une opération spéciale",
        name="Partenaire culturel associé à une opération spéciale",
    )
    event = operations_factories.SpecialEventFactory(
        externalId="fake00002",
        title=f"Jury backoffice {datetime.date.today().year}",
        offerer=venue.managingOfferer,
        venue=venue,
    )
    operations_factories.SpecialEventQuestionFactory(
        event=event,
        externalId="00002-fghij-00001",
        title="Quel âge as-tu ?",
    )
    operations_factories.SpecialEventQuestionFactory(
        event=event,
        externalId="00002-fghij-00002",
        title="Où habites-tu ?",
    )
    operations_factories.SpecialEventQuestionFactory(
        event=event,
        externalId="00002-fghij-00003",
        title="En quelques lignes, parle nous d'un module que tu apprécies particulièrement dans le backoffice et pourquoi il te plaît.",
    )
