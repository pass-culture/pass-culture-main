from pcapi.domain.beneficiary_bookings.active_mediation import ActiveMediation


def to_domain(medidation_sql_entity_view: object) -> ActiveMediation:
    return ActiveMediation(
        identifier=medidation_sql_entity_view.id,
        date_created=medidation_sql_entity_view.dateCreated,
        offer_id=medidation_sql_entity_view.offerId,
    )
