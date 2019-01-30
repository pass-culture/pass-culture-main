def has_physical_venue(offerer):
    return any([not v.isVirtual for v in offerer.managedVenues])


def has_at_least_one_user_offerer_not_validated(offerer):
    return any([uo.validationToken for uo in offerer.UserOfferers])


def has_validation_for_this_user(offerer, user):
    return any([
        uo.validationToken is None
        for uo in offerer.UserOfferers
        if uo.user == user
    ])


def is_offerer_created_from_sandbox(offerer):
    return offerer.siren[:3] == '222'


def is_93_offerer(offerer):
    return offerer.postalCode[:2] == '93'


def is_93_venue(venue):
    return venue.postalCode[:2] == '93'


def should_skip_when_validated_offerer_and_user_signed_with_not_validated_offerer(offerer, user_name):
    if offerer.validationToken is None \
        and (
                "has-signed-up-with-not-registered-offerer" in user_name \
                or "has-signed-up-with-not-validated-registered-offerer"  in user_name \
                or "has-validated-email-with-not-registered-offerer" in user_name \
                or "has-validated-email-with-not-validated-registered-offerer" in user_name
        ):
        return True


def should_skip_when_not_validated_offerer_and_user_signed_with_validated_offerer(offerer, user_name):
    if offerer.validationToken is not None \
        and (
                "has-signed-up-with-validated-registered-offerer" in user_name \
                or "has-validated-email-with-validated-registered-offerer" in user_name
        ):
        return True


def should_have_user_offerer_with_validation_token(offerer, user_name):
    if offerer.validationToken is not None:
        return True

    if "has-validated-previous-not-registered-offerer" in user_name \
        or "has-validated-previous-not-validated-registered-offerer" in user_name \
        or "has-validated-previous-validated-registered-offerer" in user_name:
        return False

    return True
