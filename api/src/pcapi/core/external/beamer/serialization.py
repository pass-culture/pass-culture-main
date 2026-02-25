from pcapi.core.external.attributes.models import ProAttributes


def format_pro_attributes(pro_attributes: ProAttributes) -> dict:
    return {
        "userId": pro_attributes.user_id,
        "DMS_APPLICATION_APPROVED": pro_attributes.dms_application_approved,
        "DMS_APPLICATION_SUBMITTED": pro_attributes.dms_application_submitted,
        "HAS_BANNER_URL": pro_attributes.has_banner_url,
        "HAS_BOOKINGS": pro_attributes.has_bookings,
        "HAS_COLLECTIVE_OFFERS": pro_attributes.has_collective_offers,
        "HAS_OFFERS": pro_attributes.has_offers,
        "HAS_INDIVIDUAL_OFFERS": pro_attributes.has_individual_offers,
        "IS_ACTIVE_PRO": pro_attributes.is_active_pro,
        "IS_BOOKING_EMAIL": pro_attributes.is_booking_email,
        "IS_EAC": pro_attributes.is_eac,
        "IS_PERMANENT": pro_attributes.isPermanent,
        "IS_OPEN_TO_PUBLIC": pro_attributes.isOpenToPublic,
        "IS_PRO": pro_attributes.is_pro,
        "IS_VIRTUAL": pro_attributes.isVirtual,
        "OFFERER_NAME": ";".join(pro_attributes.offerers_names),
        "OFFERER_TAG": ";".join(pro_attributes.offerers_tags),
        "USER_IS_ATTACHED": pro_attributes.user_is_attached,
        "VENUE_LABEL": ";".join(pro_attributes.venues_labels),
        "VENUE_TYPE": ";".join(pro_attributes.venues_types),
    }
