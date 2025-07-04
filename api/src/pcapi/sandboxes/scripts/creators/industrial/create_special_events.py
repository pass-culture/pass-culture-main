import datetime
import logging

from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.operations import factories as operations_factories
from pcapi.core.users import factories as users_factories
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)


@log_func_duration
def create_special_events() -> None:
    logger.info("create_special_events")

    _create_special_event_with_date()
    _create_special_event_with_venue()

    logger.info("created special events")


def _create_special_event_with_date() -> None:
    tag_book_club = users_factories.UserTagFactory(label="Membre du book club")
    tag_cine_club = users_factories.UserTagFactory(label="Membre du ciné club")
    event_date = datetime.date.today() + datetime.timedelta(days=15)
    event = operations_factories.SpecialEventFactory.create(
        externalId="fake00001", title="Jeu concours : gagne une place de concert", eventDate=event_date
    )
    date_question = operations_factories.SpecialEventQuestionFactory.create(
        event=event,
        externalId="00001-abcde-00001",
        title=f"Es-tu disponible le {event_date.strftime('%d/%m/%Y')} à 20h30 ?",
    )
    address_question = operations_factories.SpecialEventQuestionFactory.create(
        event=event,
        externalId="00001-abcde-00002",
        title="Où habites-tu ?",
    )
    why_question = operations_factories.SpecialEventQuestionFactory.create(
        event=event,
        externalId="00001-abcde-00003",
        title="Explique-nous pourquoi tu souhaites être sélectionné !",
    )

    good_response = operations_factories.SpecialEventResponseFactory.create(
        event=event, user__tags=[tag_book_club, tag_cine_club]
    )
    operations_factories.SpecialEventAnswerFactory.create(
        responseId=good_response.id, questionId=date_question.id, text="Oui !"
    )
    operations_factories.SpecialEventAnswerFactory.create(
        responseId=good_response.id, questionId=address_question.id, text="À la Baule !"
    )
    operations_factories.SpecialEventAnswerFactory.create(
        responseId=good_response.id, questionId=why_question.id, text="Parce que j'adore la squad interne !"
    )

    terrible_response = operations_factories.SpecialEventResponseFactory.create(event=event, user__tags=[tag_book_club])
    operations_factories.SpecialEventAnswerFactory.create(
        responseId=terrible_response.id, questionId=date_question.id, text="Non, je boude."
    )
    operations_factories.SpecialEventAnswerFactory.create(
        responseId=terrible_response.id, questionId=why_question.id, text="Je veux pas parce que je boude."
    )

    long_response = operations_factories.SpecialEventResponseFactory.create(event=event, user__tags=[tag_cine_club])
    operations_factories.SpecialEventAnswerFactory.create(
        responseId=long_response.id, questionId=date_question.id, text="Je suis tout à fait disponible"
    )
    operations_factories.SpecialEventAnswerFactory.create(
        responseId=long_response.id,
        questionId=address_question.id,
        text="3 rue de Valois 75001 Paris France Terre Voie Lactée",
    )
    operations_factories.SpecialEventAnswerFactory.create(
        responseId=long_response.id,
        questionId=why_question.id,
        text="Vous savez, moi je ne crois pas qu'il y ait de bonne ou de mauvaise situation. "
        "Moi, si je devais résumer ma vie aujourd'hui avec vous, je dirais que c'est d'abord des rencontres. "
        "Des gens qui m'ont tendu la main, peut-être à un moment où je ne pouvais pas, où j'étais seul chez moi. "
        "Et c'est assez curieux de se dire que les hasards, les rencontres, forgent une destinée... "
        "Parce que quand on a le goût de la chose, quand on a le goût de la chose bien faite, le beau geste, "
        "parfois on ne trouve pas l'interlocuteur en face je dirais, le miroir qui vous aide à avancer. "
        "Alors ça n'est pas mon cas, comme je disais là, puisque moi au contraire, j'ai pu : et je dis merci à la vie, "
        "je lui dis merci, je chante la vie, je danse la vie... je ne suis qu'amour ! "
        "Et finalement, quand beaucoup de gens aujourd'hui me disent « Mais comment fais-tu pour avoir cette humanité ? », "
        "et bien je leur réponds très simplement, je leur dis que c'est ce goût de l'amour ce goût donc qui m'a poussé aujourd'hui à entreprendre une construction mécanique, mais demain qui sait ? "
        "Peut-être simplement à me mettre au service de la communauté, à faire le don, le don de soi...",
    )


def _create_special_event_with_venue() -> None:
    venue = offerers_factories.VenueFactory.create(
        managingOfferer__name="Structure associée à une opération spéciale",
        name="Partenaire culturel associé à une opération spéciale",
    )
    event = operations_factories.SpecialEventFactory.create(
        externalId="fake00002",
        title=f"Jury backoffice {datetime.date.today().year}",
        offerer=venue.managingOfferer,
        venue=venue,
    )
    date_question = operations_factories.SpecialEventQuestionFactory.create(
        event=event,
        externalId="00002-fghij-00001",
        title="Quel âge as-tu ?",
    )
    address_question = operations_factories.SpecialEventQuestionFactory.create(
        event=event,
        externalId="00002-fghij-00002",
        title="Où habites-tu ?",
    )
    why_question = operations_factories.SpecialEventQuestionFactory.create(
        event=event,
        externalId="00002-fghij-00003",
        title="En quelques lignes, parle nous d'un module que tu apprécies particulièrement dans le backoffice et pourquoi il te plaît.",
    )

    response_from_unknown_email = operations_factories.SpecialEventResponseNoUserFactory.create(event=event)
    operations_factories.SpecialEventAnswerFactory.create(
        responseId=response_from_unknown_email.id, questionId=date_question.id, text="Où suis-je ?"
    )
    operations_factories.SpecialEventAnswerFactory.create(
        responseId=response_from_unknown_email.id,
        questionId=address_question.id,
        text="Mais qu'est-ce que je fais-là ?",
    )
    operations_factories.SpecialEventAnswerFactory.create(
        responseId=response_from_unknown_email.id, questionId=why_question.id, text="Sortez-moi de là !"
    )
