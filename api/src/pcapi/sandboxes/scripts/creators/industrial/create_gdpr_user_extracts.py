from datetime import datetime
import logging

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def create_gdpr_user_extract_data() -> None:
    logger.info("create_gdpr_user_extract_data")

    author = (
        db.session.query(users_models.User)
        .filter(users_models.User.has_admin_role)
        .order_by(users_models.User.id)
        .first()
    )
    list_beneficiary = (
        db.session.query(users_models.User)
        .filter(users_models.User.has_beneficiary_role)
        .order_by(users_models.User.id)
        .limit(2)
        .all()
    )
    list_underage_beneficiary = (
        db.session.query(users_models.User)
        .filter(users_models.User.has_underage_beneficiary_role)
        .order_by(users_models.User.id)
        .first()
    )

    users_factories.GdprUserDataExtractBeneficiaryFactory.create(user=list_beneficiary[0], authorUser=author)
    users_factories.GdprUserDataExtractBeneficiaryFactory.create(user=list_underage_beneficiary, authorUser=author)
    users_factories.GdprUserDataExtractBeneficiaryFactory.create(
        user=list_beneficiary[1], authorUser=author, dateProcessed=datetime.utcnow()
    )

    logger.info("created GDPR users extract data")
