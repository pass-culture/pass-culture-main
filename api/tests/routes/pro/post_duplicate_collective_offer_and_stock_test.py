import pytest

from pcapi.core.educational import models as educational_models
import pcapi.core.educational.factories as educational_factories
import pcapi.core.offerers.factories as offerers_factories
from pcapi.models import offer_mixin
from pcapi.models import validation_status_mixin
from pcapi.utils.date import format_into_utc_date
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    def test_duplicate_collective_offer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue)
        offer_id = offer.id
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        # When

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        # Then
        assert response.status_code == 201
        duplicate = educational_models.CollectiveOffer.query.filter_by(id=dehumanize(response.json["id"])).one()
        assert response.json == {
            "audioDisabilityCompliant": False,
            "mentalDisabilityCompliant": False,
            "motorDisabilityCompliant": False,
            "visualDisabilityCompliant": False,
            "id": humanize(duplicate.id),
            "bookingEmails": [
                "collectiveofferfactory+booking@example.com",
                "collectiveofferfactory+booking@example2.com",
            ],
            "dateCreated": format_into_utc_date(duplicate.dateCreated),
            "description": offer.description,
            "durationMinutes": None,
            "students": ["Lycée - Seconde"],
            "offerVenue": {"addressType": "other", "otherAddress": "1 rue des polissons, Paris 75017", "venueId": ""},
            "contactEmail": "collectiveofferfactory+contact@example.com",
            "contactPhone": "+33199006328",
            "hasBookingLimitDatetimesPassed": False,
            "offerId": None,
            "isActive": True,
            "isEditable": True,
            "nonHumanizedId": duplicate.id,
            "name": offer.name,
            "subcategoryId": offer.subcategoryId,
            "venue": {
                "audioDisabilityCompliant": False,
                "mentalDisabilityCompliant": False,
                "motorDisabilityCompliant": False,
                "visualDisabilityCompliant": False,
                "address": "1 boulevard Poissonnière",
                "bookingEmail": venue.bookingEmail,
                "city": "Paris",
                "comment": None,
                "dateCreated": format_into_utc_date(venue.dateCreated),
                "dateModifiedAtLastProvider": format_into_utc_date(venue.dateModifiedAtLastProvider),
                "departementCode": "75",
                "fieldsUpdated": [],
                "id": humanize(venue.id),
                "idAtProviders": None,
                "isVirtual": False,
                "lastProviderId": None,
                "latitude": 48.87004,
                "longitude": 2.3785,
                "managingOfferer": {
                    "address": "1 boulevard Poissonnière",
                    "city": "Paris",
                    "dateCreated": format_into_utc_date(venue.managingOfferer.dateCreated),
                    "dateModifiedAtLastProvider": format_into_utc_date(
                        venue.managingOfferer.dateModifiedAtLastProvider
                    ),
                    "id": humanize(offerer.id),
                    "idAtProviders": None,
                    "isActive": True,
                    "isValidated": True,
                    "lastProviderId": None,
                    "name": venue.managingOfferer.name,
                    "postalCode": "75000",
                    "siren": venue.managingOfferer.siren,
                    "thumbCount": 0,
                },
                "managingOffererId": humanize(offerer.id),
                "name": venue.name,
                "postalCode": "75000",
                "publicName": venue.publicName,
                "siret": venue.siret,
                "thumbCount": 0,
                "venueLabelId": None,
            },
            "venueId": humanize(offer.venueId),
            "status": "ACTIVE",
            "domains": [],
            "interventionArea": ["93", "94", "95"],
            "isCancellable": False,
            "imageCredit": None,
            "imageUrl": None,
            "isBookable": True,
            "collectiveStock": {
                "id": humanize(duplicate.collectiveStock.id),
                "isBooked": False,
                "isCancellable": False,
                "beginningDatetime": format_into_utc_date(offer.collectiveStock.beginningDatetime),
                "bookingLimitDatetime": format_into_utc_date(offer.collectiveStock.bookingLimitDatetime),
                "price": 100.0,
                "numberOfTickets": 25,
                "educationalPriceDetail": None,
                "isEducationalStockEditable": True,
            },
            "institution": None,
            "isVisibilityEditable": True,
            "templateId": None,
            "lastBookingStatus": None,
            "lastBookingId": None,
            "teacher": None,
            "isPublicApi": False,
        }

    def test_duplicate_collective_offer_draft_offer(self, client):
        # Given
        offerer = offerers_factories.OffererFactory()
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(
            venue=venue,
            validation=offer_mixin.OfferValidationStatus.DRAFT,
        )
        offer_id = offer.id
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        # When

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        assert response.status_code == 403
        assert response.json == {"validation": ["l'offre ne passe pas la validation"]}

    def test_duplicate_collective_offer_offerer_not_validated(self, client):
        # Given
        offerer = offerers_factories.OffererFactory(
            validationStatus=validation_status_mixin.ValidationStatus.REJECTED,
        )
        offerers_factories.UserOffererFactory(offerer=offerer, user__email="user@example.com")
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        offer = educational_factories.CollectiveOfferFactory(venue=venue)
        offer_id = offer.id
        educational_factories.CollectiveStockFactory(collectiveOffer=offer)

        # When

        response = client.with_session_auth("user@example.com").post(f"/collective/offers/{offer_id}/duplicate")

        assert response.status_code == 403
        assert response.json == {"offerer": ["la structure n'est pas autorisée à dupliquer l'offre"]}
