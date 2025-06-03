import logging

from pcapi.core.users import factories as users_factories


logger = logging.getLogger(__name__)


def create_industrial_user_tags() -> None:
    logger.info("create_industrial_user_tags")

    ambassadeurs = users_factories.UserTagCategoryFactory(name="ambassadeurs", label="Ambassadeurs")
    club = users_factories.UserTagCategoryFactory(name="club", label="Club")

    users_factories.UserTagFactory(name="ambassadeur2023", label="Ambassadeurs 2023", categories=[ambassadeurs])
    users_factories.UserTagFactory(name="ambassadeur2024", label="Ambassadeurs 2024", categories=[ambassadeurs])
    users_factories.UserTagFactory(name="ambassadeur2025", label="Ambassadeurs 2025", categories=[ambassadeurs])

    users_factories.UserTagFactory(name="clublivres", label="Club livre", categories=[club])
    users_factories.UserTagFactory(name="clubcinema", label="Club cinéma", categories=[club])
    users_factories.UserTagFactory(name="club2000", label="Club 2000", categories=[club])
