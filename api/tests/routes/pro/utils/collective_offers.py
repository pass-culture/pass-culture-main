from pcapi.core.educational import models


def expected_collective_offer_serialization(offer: models.CollectiveOffer) -> dict:
    return {
        "stock": _expected_stock_serialization(offer),
        "educationalPriceDetail": _expected_price_detail_serialization(offer),
        "educationalInstitution": _expected_institution_serialization(offer),
        "teacher": _expected_teacher_serialization(offer),
        **_shared_field_serialization(offer),
    }


def expected_collective_offer_template_serialization(offer: models.CollectiveOfferTemplate) -> dict:
    return {
        "educationalPriceDetail": None,
        **_shared_field_serialization(offer),
    }


def _expected_stock_serialization(offer: models.CollectiveOffer) -> dict:
    stock = offer.collectiveStock
    if not stock:
        return {}
    return {
        "beginningDatetime": stock.beginningDatetime.isoformat(),
        "bookingLimitDatetime": stock.bookingLimitDatetime.isoformat(),
        "id": stock.id,
        "isBookable": True,
        "price": int(stock.price * 100),  # convert to cents
        "educationalPriceDetail": stock.priceDetail,
        "numberOfTickets": stock.numberOfTickets,
    }


def _expected_price_detail_serialization(offer: models.CollectiveOffer) -> str | None:
    stock = offer.collectiveStock
    if not stock:
        return None
    return stock.priceDetail


def _expected_institution_serialization(offer: models.CollectiveOffer) -> dict | None:
    institution = offer.institution
    if not institution:
        return None
    return {
        "id": institution.id,
        "institutionType": institution.institutionType,
        "name": institution.name,
        "city": institution.city,
        "postalCode": institution.postalCode,
    }


def _expected_teacher_serialization(offer: models.CollectiveOffer) -> dict | None:
    teacher = offer.teacher
    if not teacher:
        return None
    return {
        "email": teacher.email,
        "firstName": teacher.firstName,
        "lastName": teacher.lastName,
        "civility": teacher.civility,
    }


def _expected_venue_serialization(offer: models.CollectiveOffer) -> dict:
    venue = offer.venue
    return {
        "address": venue.address,
        "city": venue.city,
        "coordinates": {"latitude": float(venue.latitude), "longitude": float(venue.longitude)},
        "id": venue.id,
        "name": venue.name,
        "postalCode": "75000",
        "publicName": venue.publicName,
        "managingOfferer": {"name": venue.managingOfferer.name},
    }


def _expected_national_program_serialization(offer: models.CollectiveOffer) -> dict | None:
    national_program = offer.nationalProgram
    if not national_program:
        return None
    return {"id": national_program.id, "name": national_program.name}


def _expected_offer_venue_serialization(offer: models.CollectiveOffer) -> dict:
    offer_venue = offer.offerVenue
    return {
        "addressType": offer_venue["addressType"],
        "address": offer_venue.get("address"),
        "city": offer_venue.get("city"),
        "name": offer_venue.get("name"),
        "otherAddress": offer_venue.get("otherAddress"),
        "postalCode": offer_venue.get("postalCode"),
        "publicName": offer_venue.get("publicName"),
        "venueId": offer_venue.get("venueId"),
    }


def _shared_field_serialization(offer: models.CollectiveOffer) -> dict:
    if offer.domains:
        domains = [{"id": domain.id, "name": domain.name} for domain in offer.domains]
    else:
        domains = []

    students = [student.value for student in offer.students]

    return {
        "id": offer.id,
        "description": offer.description,
        "isExpired": False,
        "isSoldOut": False,
        "name": offer.name,
        "venue": _expected_venue_serialization(offer),
        "subcategoryLabel": offer.subcategory.app_label,
        "durationMinutes": offer.durationMinutes,
        "audioDisabilityCompliant": offer.audioDisabilityCompliant,
        "mentalDisabilityCompliant": offer.mentalDisabilityCompliant,
        "motorDisabilityCompliant": offer.motorDisabilityCompliant,
        "visualDisabilityCompliant": offer.visualDisabilityCompliant,
        "contactEmail": offer.contactEmail,
        "contactPhone": offer.contactPhone,
        "offerVenue": _expected_offer_venue_serialization(offer),
        "domains": domains,
        "interventionArea": offer.interventionArea,
        "imageCredit": offer.imageCredit,
        "imageUrl": offer.imageUrl,
        "offerId": offer.offerId,
        "students": students,
        "nationalProgram": _expected_national_program_serialization(offer),
    }
