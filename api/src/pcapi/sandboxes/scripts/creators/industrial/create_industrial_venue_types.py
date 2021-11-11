import logging

from pcapi.core.offerers.factories import VenueTypeFactory
from pcapi.core.offerers.models import VenueType


logger = logging.getLogger(__name__)


def create_industrial_venue_types() -> list[VenueType]:
    logger.info("create_industrial_venue_types")

    labels = [
        "Arts visuels, arts plastiques et galeries",
        "Centre culturel",
        "Cours et pratique artistiques",
        "Culture scientifique",
        "Festival",
        "Jeux / Jeux vidéos",
        "Librairie",
        "Bibliothèque ou médiathèque",
        "Musée",
        "Musique - Disquaire",
        "Musique - Magasin d’instruments",
        "Musique - Salle de concerts",
        "Offre numérique",
        "Patrimoine et tourisme",
        "Cinéma - Salle de projections",
        "Spectacle vivant",
        "Autre",
    ]

    venue_types = [VenueTypeFactory(label=label) for label in labels]

    logger.info("created %i venue types", len(venue_types))

    return venue_types
