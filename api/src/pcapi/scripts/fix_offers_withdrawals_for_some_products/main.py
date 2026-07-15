"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=cnormant/pc-41731 \
  -f NAMESPACE=fix_offers_withdrawals_for_some_products \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.core.categories import subcategories
from pcapi.core.offers.models import Offer
from pcapi.core.offers.models import WithdrawalTypeEnum
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    NON_EVENT_SUBCATEGORIES = [
        subcategory.id
        for subcategory in subcategories.ALL_SUBCATEGORIES
        if not subcategory.is_event and subcategory.is_selectable
    ]
    venue_ids = [9872, 80646, 24273, 20136, 20741, 10673, 3748, 14433, 10776, 9985, 24273, 145919, 150770, 24273]

    # print(NON_EVENT_SUBCATEGORIES)
    # ['ABO_BIBLIOTHEQUE', 'ABO_CONCERT', 'ABO_JEU_VIDEO', 'ABO_LIVRE_NUMERIQUE', 'ABO_LUDOTHEQUE', 'ABO_MEDIATHEQUE', 'ABO_PLATEFORME_MUSIQUE', 'ABO_PLATEFORME_VIDEO', 'ABO_PRATIQUE_ART', 'ABO_PRESSE_EN_LIGNE', 'ABO_SPECTACLE', 'ACHAT_INSTRUMENT', 'ACTIVATION_THING', 'APP_CULTURELLE', 'AUTRE_SUPPORT_NUMERIQUE', 'BON_ACHAT_INSTRUMENT', 'CAPTATION_MUSIQUE', 'CARTE_CINE_ILLIMITE', 'CARTE_CINE_MULTISEANCES', 'CARTE_JEUNES', 'CARTE_MUSEE', 'CINE_VENTE_DISTANCE', 'ESCAPE_GAME', 'JEU_EN_LIGNE', 'JEU_SUPPORT_PHYSIQUE', 'LIVRE_AUDIO_PHYSIQUE', 'LIVRE_NUMERIQUE', 'LIVRE_PAPIER', 'LOCATION_INSTRUMENT', 'MATERIEL_ART_CREATIF', 'MUSEE_VENTE_DISTANCE', 'OEUVRE_ART', 'PARTITION', 'PLATEFORME_PRATIQUE_ARTISTIQUE', 'PRATIQUE_ART_VENTE_DISTANCE', 'PODCAST', 'SPECTACLE_ENREGISTRE', 'SPECTACLE_VENTE_DISTANCE', 'SUPPORT_PHYSIQUE_FILM', 'SUPPORT_PHYSIQUE_MUSIQUE_CD', 'SUPPORT_PHYSIQUE_MUSIQUE_VINYLE', 'TELECHARGEMENT_LIVRE_AUDIO', 'TELECHARGEMENT_MUSIQUE', 'VISITE_VIRTUELLE', 'VOD']

    updated_count = 0
    for venue_id in venue_ids:
        offers_query = db.session.query(Offer).filter(
            Offer.withdrawalType == WithdrawalTypeEnum.NO_TICKET, Offer.venueId == venue_id
        )

        updated_count += offers_query.filter(
            sa.or_(Offer.withdrawalDetails.is_(None), Offer.withdrawalDetails == ""),
            Offer.subcategoryId.in_(NON_EVENT_SUBCATEGORIES),
        ).update({Offer.withdrawalType: None}, synchronize_session=False)
        db.session.flush()

        other_offers_query = offers_query.filter(Offer.withdrawalDetails.is_not(None), Offer.venueId == venue_id)
        # Set withdrawalType to ON_SITE for offers with withdrawalDetails
        updated_count += other_offers_query.update(
            {Offer.withdrawalType: WithdrawalTypeEnum.ON_SITE}, synchronize_session=False
        )
        db.session.flush()

    logger.info("Successfully updated %s offers", updated_count)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main()

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
