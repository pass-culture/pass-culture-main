from pcapi.core.educational import factories as educational_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offers import factories as offers_factories
from pcapi.core.offers import models as offers_models


def create_industrial_offerer_confidence_rules() -> None:
    rule1 = offerers_factories.ManualReviewOffererConfidenceRuleFactory(
        offerer__name="Structure en validation manuelle",
    )
    venue1 = offerers_factories.VenueFactory(
        managingOfferer=rule1.offerer,
        name="Lieu de la structure en validation manuelle",
    )
    offers_factories.ThingStockFactory(
        offer__name="Offre de la structure en validation manuelle",
        offer__venue=venue1,
        offer__isActive=False,
        offer__validation=offers_models.OfferValidationStatus.PENDING,
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name="Offre collective de la structure en validation manuelle",
        collectiveOffer__venue=venue1,
        collectiveOffer__isActive=False,
        collectiveOffer__validation=offers_models.OfferValidationStatus.PENDING,
    )

    rule2 = offerers_factories.WhitelistedOffererConfidenceRuleFactory(
        offerer__name="Structure de confiance",
    )
    venue2 = offerers_factories.VenueFactory(managingOfferer=rule2.offerer, name="Lieu de la structure de confiance")
    offers_factories.ThingStockFactory(
        offer__name="Offre de la structure de confiance",
        offer__venue=venue2,
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name="Offre collective de la structure de confiance",
        collectiveOffer__venue=venue2,
    )

    offerer = offerers_factories.OffererFactory(name="Structure avec des règles de fraude sur les lieux")
    rule3 = offerers_factories.ManualReviewVenueConfidenceRuleFactory(
        venue__managingOfferer=offerer,
        venue__name="Lieu en validation manuelle",
    )
    offers_factories.ThingStockFactory(
        offer__name="Offre du lieu en validation manuelle",
        offer__venue=rule3.venue,
        offer__isActive=False,
        offer__validation=offers_models.OfferValidationStatus.PENDING,
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name="Offre collective du lieu en validation manuelle",
        collectiveOffer__venue=rule3.venue,
        collectiveOffer__isActive=False,
        collectiveOffer__validation=offers_models.OfferValidationStatus.PENDING,
    )
    rule4 = offerers_factories.WhitelistedVenueConfidenceRuleFactory(
        venue__managingOfferer=offerer,
        venue__name="Lieu de confiance",
    )
    offers_factories.ThingStockFactory(
        offer__name="Offre du lieu de confiance",
        offer__venue=rule4.venue,
    )
    educational_factories.CollectiveStockFactory(
        collectiveOffer__name="Offre collective du lieu de confiance",
        collectiveOffer__venue=rule4.venue,
    )
