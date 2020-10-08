from typing import List

from pcapi.models.venue_type import VenueType
from pcapi.repository import repository
from pcapi.model_creators.generic_creators import create_venue_type
from pcapi.utils.logger import logger


def create_industrial_venue_types() -> List[VenueType]:
    logger.info('create_industrial_venue_types')

    labels = [
        'Arts visuels, arts plastiques et galeries',
        'Centre culturel',
        'Cours et pratique artistiques',
        'Culture scientifique',
        'Festival',
        'Jeux / Jeux vidéos',
        'Librairie',
        'Bibliothèque ou médiathèque',
        'Musée',
        'Musique - Disquaire',
        'Musique - Magasin d’instruments',
        'Musique - Salle de concerts',
        'Offre numérique',
        'Patrimoine et tourisme',
        'Cinéma - Salle de projections',
        'Spectacle vivant',
        'Autre'
    ]

    venue_types = [create_venue_type(label=label) for label in labels]

    repository.save(*venue_types)

    logger.info(f'created {len(venue_types)} venue types')

    return venue_types
