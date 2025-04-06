"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-35227-check-domains-national-programs/api/src/pcapi/scripts/check_national_program/main.py

"""

import csv
import logging
import os

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    domains: "sa_orm.Query[educational_models.EducationalDomain]" = db.session.query(
        educational_models.EducationalDomain
    ).options(sa_orm.selectinload(educational_models.EducationalDomain.nationalPrograms))
    program_ids_by_domain_id = {
        domain.id: [program.id for program in domain.nationalPrograms if program.isActive] for domain in domains
    }

    collective_offers: "sa_orm.Query[educational_models.CollectiveOffer]" = (
        db.session.query(educational_models.CollectiveOffer)
        .filter(educational_models.CollectiveOffer.nationalProgramId.is_not(None))
        .options(sa_orm.selectinload(educational_models.CollectiveOffer.domains))
    )

    collective_offer_templates: "sa_orm.Query[educational_models.CollectiveOfferTemplate]" = (
        db.session.query(educational_models.CollectiveOfferTemplate)
        .filter(educational_models.CollectiveOfferTemplate.nationalProgramId.is_not(None))
        .options(sa_orm.selectinload(educational_models.CollectiveOfferTemplate.domains))
    )

    invalid_offers = []
    for collective_offer in collective_offers.yield_per(1000):
        if len(collective_offer.domains) == 0:
            invalid_offers.append(collective_offer)
            continue

        valid_program_ids = {
            program_id for domain in collective_offer.domains for program_id in program_ids_by_domain_id[domain.id]
        }
        if collective_offer.nationalProgramId not in valid_program_ids:
            invalid_offers.append(collective_offer)

    invalid_offer_templates = []
    for collective_offer_template in collective_offer_templates.yield_per(1000):
        if len(collective_offer_template.domains) == 0:
            invalid_offer_templates.append(collective_offer_template)
            continue

        valid_program_ids = {
            program_id
            for domain in collective_offer_template.domains
            for program_id in program_ids_by_domain_id[domain.id]
        }
        if collective_offer_template.nationalProgramId not in valid_program_ids:
            invalid_offer_templates.append(collective_offer_template)

    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/invalid_collective_offers.csv", "w", encoding="utf8") as f:
        header = ["id", "offer_type", "program_id", "domain_ids", "provider_id"]
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

        for collective_offer in collective_offers:
            writer.writerow(
                {
                    "id": collective_offer.id,
                    "offer_type": "BOOKABLE",
                    "program_id": collective_offer.nationalProgramId,
                    "domain_ids": ", ".join([str(domain.id) for domain in collective_offer.domains]),
                    "provider_id": collective_offer.providerId,
                }
            )

        for collective_offer_template in collective_offer_templates:
            writer.writerow(
                {
                    "id": collective_offer_template.id,
                    "offer_type": "TEMPLATE",
                    "program_id": collective_offer_template.nationalProgramId,
                    "domain_ids": ", ".join([str(domain.id) for domain in collective_offer_template.domains]),
                    "provider_id": collective_offer_template.providerId,
                }
            )


if __name__ == "__main__":
    app.app_context().push()

    main()
