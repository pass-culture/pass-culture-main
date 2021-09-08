import datetime

import factory

from . import models


class BeneficiaryPreSubscriptionFactory(factory.Factory):
    class Meta:
        model = models.BeneficiaryPreSubscription

    date_of_birth = datetime.datetime(1995, 2, 5)
    activity: str = "Apprenti"
    address: str = "3 rue de Valois"
    application_id: str = "12"
    city: str = "Paris"
    postal_code: str = "35123"
    email: str = "rennes@example.org"
    first_name: str = "Thomas"
    civility: str = "Mme"
    last_name: str = "DURAND"
    phone_number: str = "0123456789"
    source: str = "jouve"
    source_id: str = None
    id_piece_number: str = "140767100016"
    fraud_fields = factory.LazyAttribute(lambda x: [])
