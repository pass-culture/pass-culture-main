"""
The main goal of this module is to provide a safe way to change the way a
venue's type was handled: from a venue_type table with one 'label' field which
was updated from time to time, to a more centralised enum-based approach.

Therefore this code should not be used after this shift is done, it might break
because of column and/or table (little) changes or be incomplete because of
missing codes and/or labels.
"""
import logging

from sqlalchemy import exc

from pcapi.models import db


logger = logging.getLogger(__name__)


UPDATE_VENUES_WITH_LABEL_SQL = """
UPDATE venue
SET "venueTypeCode" = :code
WHERE
    "id" in (
        SELECT venue.id
        FROM venue
        LEFT JOIN venue_type
            ON venue_type.id = venue."venueTypeId"
        WHERE venue_type.label = :label
    )
RETURNING id
"""


def _update_venues_with_label(code: str, label: str) -> set[int]:
    res = db.session.execute(UPDATE_VENUES_WITH_LABEL_SQL, {"code": code, "label": label})
    return {row[0] for row in res}


def update_venues_codes() -> set[int]:
    logger.info("update venues codes: start")
    codes_labels = [
        ("VISUAL_ARTS", "Arts visuels, arts plastiques et galeries"),
        ("CULTURAL_CENTRE", "Centre culturel"),
        ("ARTISTIC_COURSE", "Cours et pratique artistiques"),
        ("SCIENTIFIC_CULTURE", "Culture scientifique"),
        ("FESTIVAL", "Festival"),
        ("GAMES", "Jeux / Jeux vidéos"),
        ("BOOKSTORE", "Librairie"),
        ("LIBRARY", "Bibliothèque ou médiathèque"),
        ("MUSEUM", "Musée"),
        ("RECORD_STORE", "Musique - Disquaire"),
        ("MUSICAL_INSTRUMENT_STORE", "Musique - Magasin d’instruments"),
        ("CONCERT_HALL", "Musique - Salle de concerts"),
        ("DIGITAL", "Offre numérique"),
        ("PATRIMONY_TOURISM", "Patrimoine et tourisme"),
        ("MOVIE", "Cinéma - Salle de projections"),
        ("PERFORMING_ARTS", "Spectacle vivant"),
        ("CREATIVE_ARTS_STORE", "Magasin arts créatifs"),
        ("OTHER", "Autre"),
    ]

    updated_ids = set()
    for code, label in codes_labels:
        print(f"update venues codes: {label} -> {code} ongoing")

        try:
            updated_ids |= _update_venues_with_label(code=code, label=label)
        except exc.SQLAlchemyError as e:
            logger.exception("update venues codes: FAILURE", extra={"code": code, "label": label, "error": str(e)})
            db.session.rollback()

    db.session.commit()

    logger.info(
        "update venues codes: end", extra={"script": "update_venues_codes", "updatedIdsCount": len(updated_ids)}
    )
    return updated_ids
