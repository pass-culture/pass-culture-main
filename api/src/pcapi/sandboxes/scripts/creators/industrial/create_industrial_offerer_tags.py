import logging

from pcapi.core.offerers import factories as offerers_factories
from pcapi.routes.backoffice.home import CONFORMITE_TAG_NAME


logger = logging.getLogger(__name__)


def create_industrial_offerer_tags() -> None:
    logger.info("create_industrial_offerer_tags")

    comptage = offerers_factories.OffererTagCategoryFactory(name="comptage", label="Comptage partenaires")
    homologation = offerers_factories.OffererTagCategoryFactory(name="homologation", label="Homologation")

    offerers_factories.OffererTagFactory(name="collectivite", label="Collectivité", categories=[comptage, homologation])
    offerers_factories.OffererTagFactory(
        name="etablissement-public", label="Établissement public", categories=[comptage]
    )
    offerers_factories.OffererTagFactory(
        name="auto-entrepreneur", label="Auto-Entrepreneur", categories=[comptage, homologation]
    )
    offerers_factories.OffererTagFactory(name="festival", label="Festival", categories=[comptage])
    offerers_factories.OffererTagFactory(name="top-acteur", label="Top Acteur", categories=[homologation])
    offerers_factories.OffererTagFactory(
        name="culture-scientifique", label="Culture scientifique", categories=[homologation]
    )
    offerers_factories.OffererTagFactory(name="partenaire-national", label="Partenaire national", categories=[comptage])
    offerers_factories.OffererTagFactory(name=CONFORMITE_TAG_NAME, label="Conformité", categories=[homologation])
    offerers_factories.OffererTagFactory(name="adage", label="Adage", categories=[homologation])
    offerers_factories.OffererTagFactory(name="siren-caduc", label="SIREN caduc", categories=[homologation])
    offerers_factories.OffererTagFactory(name="non-diffusible", label="Non-diffusible", categories=[homologation])
