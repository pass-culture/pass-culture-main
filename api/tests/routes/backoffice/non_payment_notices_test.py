import datetime
from decimal import Decimal

import pytest
from flask import url_for

from pcapi.core.finance import factories as finance_factories
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db

from .helpers import html_parser
from .helpers.get import GetEndpointHelper
from .helpers.post import PostEndpointHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class ListNonPaymentNoticesTest(GetEndpointHelper):
    endpoint = "backoffice_web.non_payment_notices.list_notices"
    needed_permission = perm_models.Permissions.READ_NON_PAYMENT_NOTICES

    # - fetch session (1 query)
    # - fetch user (1 query)
    # - fetch non payment notices (1 query)
    expected_num_queries = 3

    def test_list_non_payment_notices(self, authenticated_client):
        created_notice = offerers_factories.NonPaymentNoticeFactory(
            offerer=offerers_factories.OffererFactory(), dateCreated=datetime.date.today()
        )
        pending_notice = offerers_factories.NonPaymentNoticeFactory(
            status=offerers_models.NoticeStatus.PENDING,
            noticeType=offerers_models.NoticeType.REMINDER_LETTER,
            motivation=offerers_models.NoticeStatusMotivation.OFFERER_NOT_FOUND,
            dateCreated=datetime.date.today() - datetime.timedelta(days=1),
        )
        venue = offerers_factories.VenueFactory()
        closed_notice = offerers_factories.NonPaymentNoticeFactory(
            venue=venue,
            offerer=venue.managingOfferer,
            status=offerers_models.NoticeStatus.CLOSED,
            noticeType=offerers_models.NoticeType.BAILIFF,
            motivation=offerers_models.NoticeStatusMotivation.ALREADY_PAID,
            batch=finance_factories.CashflowBatchFactory(label="VIR123"),
            dateCreated=datetime.date.today() - datetime.timedelta(days=2),
        )

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 3

        assert rows[0]["ID"] == str(created_notice.id)
        assert rows[0]["Date de création"] == created_notice.dateCreated.strftime("%d/%m/%Y")
        assert rows[0]["Date de réception"] == created_notice.dateReceived.strftime("%d/%m/%Y")
        assert rows[0]["État"] == "Nouveau"
        assert rows[0]["Type d'avis"] == "Avis d'impayé"
        assert rows[0]["Référence"] == "ABC123"
        assert rows[0]["Nom de l'émetteur"] == "Guy Ssier de Justice"
        assert rows[0]["Email de l'émetteur"] == "plus.dargent@example.com"
        assert rows[0]["Montant"] == "199,99 €"
        assert rows[0]["Entité juridique"] == created_notice.offerer.name
        assert rows[0]["Partenaire culturel"] == ""
        assert rows[0]["Motif"] == ""
        assert rows[0]["N° de virement"] == ""

        assert rows[1]["ID"] == str(pending_notice.id)
        assert rows[1]["Date de création"] == pending_notice.dateCreated.strftime("%d/%m/%Y")
        assert rows[1]["Date de réception"] == pending_notice.dateReceived.strftime("%d/%m/%Y")
        assert rows[1]["État"] == "En attente de retour"
        assert rows[1]["Type d'avis"] == "Lettre de relance"
        assert rows[1]["Référence"] == "ABC123"
        assert rows[1]["Nom de l'émetteur"] == "Guy Ssier de Justice"
        assert rows[1]["Email de l'émetteur"] == "plus.dargent@example.com"
        assert rows[1]["Montant"] == "199,99 €"
        assert rows[1]["Entité juridique"] == ""
        assert rows[1]["Partenaire culturel"] == ""
        assert rows[1]["Motif"] == "Acteur culturel introuvable"
        assert rows[1]["N° de virement"] == ""

        assert rows[2]["ID"] == str(closed_notice.id)
        assert rows[2]["Date de création"] == closed_notice.dateCreated.strftime("%d/%m/%Y")
        assert rows[2]["Date de réception"] == closed_notice.dateReceived.strftime("%d/%m/%Y")
        assert rows[2]["État"] == "Terminé"
        assert rows[2]["Type d'avis"] == "Huissier de justice"
        assert rows[2]["Référence"] == "ABC123"
        assert rows[2]["Nom de l'émetteur"] == "Guy Ssier de Justice"
        assert rows[2]["Email de l'émetteur"] == "plus.dargent@example.com"
        assert rows[2]["Montant"] == "199,99 €"
        assert rows[2]["Entité juridique"] == closed_notice.offerer.name
        assert rows[2]["Partenaire culturel"] == closed_notice.venue.name
        assert rows[2]["Motif"] == "Déjà payé"
        assert rows[2]["N° de virement"] == "VIR123"


class GetCreateNonPaymentNoticeFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.non_payment_notices.get_create_non_payment_notice_form"
    needed_permission = perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES

    def test_get_create_form_test(self, legit_user, authenticated_client):
        form_url = url_for(self.endpoint)

        with assert_num_queries(2):  # session + current user
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class CreateNonPaymentNoticeTest(PostEndpointHelper):
    endpoint = "backoffice_web.non_payment_notices.create_non_payment_notice"
    needed_permission = perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES

    def test_create_non_payment_notice(self, authenticated_client):
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "date_received": datetime.date.today() - datetime.timedelta(days=1),
                "notice_type": "BAILIFF",
                "amount": "12,34",
                "reference": "123ABC",
                "emitter_name": "Ferran Largent",
                "emitter_email": "avis.impayé@example.com",
                "offerer": "",
                "venue": "",
            },
        )

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data) == "L'avis d'impayé a été créé"
        )

        notice = db.session.query(offerers_models.NonPaymentNotice).one()
        assert notice.dateReceived == datetime.date.today() - datetime.timedelta(days=1)
        assert notice.status == offerers_models.NoticeStatus.CREATED
        assert notice.noticeType == offerers_models.NoticeType.BAILIFF
        assert notice.reference == "123ABC"
        assert notice.emitterName == "Ferran Largent"
        assert notice.emitterEmail == "avis.impayé@example.com"
        assert notice.amount == Decimal("12.34")
        assert notice.offerer is None
        assert notice.venue is None
        assert notice.motivation is None
        assert notice.batch is None

    def test_create_non_payment_notice_with_offerer_only(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "date_received": datetime.date.today() - datetime.timedelta(days=1),
                "notice_type": "BAILIFF",
                "amount": "12,34",
                "reference": "123ABC",
                "emitter_name": "Ferran Largent",
                "emitter_email": "avis.impayé@example.com",
                "offerer": offerer.id,
                "venue": "",
            },
        )

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data) == "L'avis d'impayé a été créé"
        )

        notice = db.session.query(offerers_models.NonPaymentNotice).one()
        assert notice.dateReceived == datetime.date.today() - datetime.timedelta(days=1)
        assert notice.status == offerers_models.NoticeStatus.CREATED
        assert notice.noticeType == offerers_models.NoticeType.BAILIFF
        assert notice.reference == "123ABC"
        assert notice.emitterName == "Ferran Largent"
        assert notice.emitterEmail == "avis.impayé@example.com"
        assert notice.amount == Decimal("12.34")
        assert notice.offerer == offerer
        assert notice.venue is None
        assert notice.motivation is None
        assert notice.batch is None

    def test_create_non_payment_notice_with_venue_only(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "date_received": datetime.date.today() - datetime.timedelta(days=1),
                "notice_type": "BAILIFF",
                "amount": "12,34",
                "reference": "123ABC",
                "emitter_name": "Ferran Largent",
                "emitter_email": "avis.impayé@example.com",
                "offerer": "",
                "venue": venue.id,
            },
        )

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data) == "L'avis d'impayé a été créé"
        )

        notice = db.session.query(offerers_models.NonPaymentNotice).one()
        assert notice.dateReceived == datetime.date.today() - datetime.timedelta(days=1)
        assert notice.status == offerers_models.NoticeStatus.CREATED
        assert notice.noticeType == offerers_models.NoticeType.BAILIFF
        assert notice.reference == "123ABC"
        assert notice.emitterName == "Ferran Largent"
        assert notice.emitterEmail == "avis.impayé@example.com"
        assert notice.amount == Decimal("12.34")
        assert notice.offerer == venue.managingOfferer
        assert notice.venue == venue
        assert notice.motivation is None
        assert notice.batch is None

    def test_create_non_payment_notice_with_offerer_and_venue(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory(managingOfferer=offerer)
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "date_received": datetime.date.today() - datetime.timedelta(days=1),
                "notice_type": "BAILIFF",
                "amount": "12,34",
                "reference": "123ABC",
                "emitter_name": "Ferran Largent",
                "emitter_email": "avis.impayé@example.com",
                "offerer": offerer.id,
                "venue": venue.id,
            },
        )

        assert response.status_code == 303
        assert (
            html_parser.extract_alert(authenticated_client.get(response.location).data) == "L'avis d'impayé a été créé"
        )

        notice = db.session.query(offerers_models.NonPaymentNotice).one()
        assert notice.dateReceived == datetime.date.today() - datetime.timedelta(days=1)
        assert notice.status == offerers_models.NoticeStatus.CREATED
        assert notice.noticeType == offerers_models.NoticeType.BAILIFF
        assert notice.reference == "123ABC"
        assert notice.emitterName == "Ferran Largent"
        assert notice.emitterEmail == "avis.impayé@example.com"
        assert notice.amount == Decimal("12.34")
        assert notice.offerer == offerer
        assert notice.venue == venue
        assert notice.motivation is None
        assert notice.batch is None

    def test_create_non_payment_notice_with_offerer_and_wrong_venue(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        venue = offerers_factories.VenueFactory()
        response = self.post_to_endpoint(
            authenticated_client,
            form={
                "date_received": datetime.date.today() - datetime.timedelta(days=1),
                "notice_type": "BAILIFF",
                "amount": "12,34",
                "reference": "123ABC",
                "emitter_name": "Ferran Largent",
                "emitter_email": "avis.impayé@example.com",
                "offerer": offerer.id,
                "venue": venue.id,
            },
        )

        assert response.status_code == 303
        assert "Le partenaire culturel doit être sur l'entité juridique sélectionnée" in html_parser.extract_alert(
            authenticated_client.get(response.location).data
        )

        assert db.session.query(offerers_models.NonPaymentNotice).count() == 0
