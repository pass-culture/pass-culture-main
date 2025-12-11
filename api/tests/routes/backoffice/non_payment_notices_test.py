import dataclasses
import datetime
from decimal import Decimal

import pytest
from flask import url_for

from pcapi.core.finance import factories as finance_factories
from pcapi.core.history import models as history_models
from pcapi.core.mails import testing as mails_testing
from pcapi.core.mails.transactional.sendinblue_template_ids import TransactionalEmail
from pcapi.core.offerers import factories as offerers_factories
from pcapi.core.offerers import models as offerers_models
from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import assert_num_queries
from pcapi.models import db
from pcapi.utils.date import get_date_formatted_for_email

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

    # - fetch session + user (1 query)
    # - fetch non payment notices (1 query)
    expected_num_queries = 2

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
        assert rows[0]["Type d'avis"] == "Avis de sommes à payer"
        assert rows[0]["Référence"] == created_notice.reference
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
        assert rows[1]["Référence"] == pending_notice.reference
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
        assert rows[2]["Référence"] == closed_notice.reference
        assert rows[2]["Nom de l'émetteur"] == "Guy Ssier de Justice"
        assert rows[2]["Email de l'émetteur"] == "plus.dargent@example.com"
        assert rows[2]["Montant"] == "199,99 €"
        assert rows[2]["Entité juridique"] == closed_notice.offerer.name
        assert rows[2]["Partenaire culturel"] == closed_notice.venue.name
        assert rows[2]["Motif"] == "Déjà payé"
        assert rows[2]["N° de virement"] == "VIR123"

    def test_list_notices_by_id(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory()
        offerers_factories.NonPaymentNoticeFactory()
        notice_id = str(notice.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q=notice_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == notice_id

    def test_list_notices_by_emitter_email(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory(emitterEmail="david.impaye@example.com")
        offerers_factories.NonPaymentNoticeFactory(emitterEmail="david.paye@example.com")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="david.impaye@example.com"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(notice.id)

    def test_list_notices_by_emitter_name(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory(emitterName="David Impayé")
        notice_with_close_name = offerers_factories.NonPaymentNoticeFactory(emitterName="Les Sociétés David")
        offerers_factories.NonPaymentNoticeFactory(emitterName="Rien à voir")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="David"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 2
        assert set(row["ID"] for row in rows) == {str(notice.id), str(notice_with_close_name.id)}

    def test_list_notices_by_reference(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory(reference="AZERT")
        offerers_factories.NonPaymentNoticeFactory(reference="AZERTY")

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, q="AZERT"))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(notice.id)

    def test_list_notices_by_status(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory(status=offerers_models.NoticeStatus.CLOSED)
        offerers_factories.NonPaymentNoticeFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(url_for(self.endpoint, status=offerers_models.NoticeStatus.CLOSED.name))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(notice.id)

    def test_list_notices_by_type(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory(noticeType=offerers_models.NoticeType.BAILIFF)
        offerers_factories.NonPaymentNoticeFactory()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(self.endpoint, notice_type=offerers_models.NoticeType.BAILIFF.name)
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(notice.id)

    def test_list_notices_by_batch(self, authenticated_client):
        batch = finance_factories.CashflowBatchFactory()
        notice = offerers_factories.NonPaymentNoticeFactory(batch=batch)
        offerers_factories.NonPaymentNoticeFactory(batch=finance_factories.CashflowBatchFactory())
        offerers_factories.NonPaymentNoticeFactory()
        batch_id = str(batch.id)

        # one more query because of cashflow_batches validation
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, batch=batch_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(notice.id)

    def test_list_notices_by_venue(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        notice = offerers_factories.NonPaymentNoticeFactory(venue=venue)
        offerers_factories.NonPaymentNoticeFactory(venue=offerers_factories.VenueFactory())
        offerers_factories.NonPaymentNoticeFactory()
        venue_id = str(venue.id)

        # one more query because of venue validation
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, venue=venue_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(notice.id)

    def test_list_notices_by_offerer(self, authenticated_client):
        offerer = offerers_factories.OffererFactory()
        notice = offerers_factories.NonPaymentNoticeFactory(offerer=offerer)
        offerers_factories.NonPaymentNoticeFactory(offerer=offerers_factories.OffererFactory())
        offerers_factories.NonPaymentNoticeFactory()
        offerer_id = str(offerer.id)

        # one more query because of offerer validation
        with assert_num_queries(self.expected_num_queries + 1):
            response = authenticated_client.get(url_for(self.endpoint, offerer=offerer_id))
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(notice.id)

    def test_list_notices_by_dates(self, authenticated_client):
        now = datetime.datetime(2025, 6, 5)
        notice = offerers_factories.NonPaymentNoticeFactory(dateReceived=now - datetime.timedelta(days=2))
        offerers_factories.NonPaymentNoticeFactory(dateReceived=now - datetime.timedelta(days=4))
        offerers_factories.NonPaymentNoticeFactory(dateReceived=now)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(
                url_for(
                    self.endpoint,
                    from_to_date="02/06/2025 - 04/06/2025",
                )
            )
            assert response.status_code == 200

        rows = html_parser.extract_table_rows(response.data)
        assert len(rows) == 1
        assert rows[0]["ID"] == str(notice.id)


class GetCreateNonPaymentNoticeFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.non_payment_notices.get_create_non_payment_notice_form"
    needed_permission = perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES

    def test_get_create_form_test(self, authenticated_client):
        form_url = url_for(self.endpoint)

        with assert_num_queries(1):  # session
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
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "L'avis d'impayé a été enregistré"
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

        # No action when not associated with offerer nor venue
        assert db.session.query(history_models.ActionHistory).count() == 0

    def test_create_non_payment_notice_with_offerer_only(self, authenticated_client, legit_user):
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
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "L'avis d'impayé a été enregistré"
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

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.NON_PAYMENT_NOTICE_CREATED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.offererId == offerer.id
        assert action.venueId is None
        assert action.extraData == {"non_payment_notice_id": notice.id}

    @pytest.mark.parametrize(
        "venue_factory", [offerers_factories.VenueFactory, offerers_factories.VenueWithoutSiretFactory]
    )
    def test_create_non_payment_notice_with_venue_only(self, authenticated_client, legit_user, venue_factory):
        venue = venue_factory()
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
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "L'avis d'impayé a été enregistré"
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

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.NON_PAYMENT_NOTICE_CREATED
        assert action.actionDate.date() == datetime.date.today()
        assert action.authorUserId == legit_user.id
        assert action.offererId == venue.managingOfferer.id
        assert action.venueId == venue.id
        assert action.extraData == {"non_payment_notice_id": notice.id}

    @pytest.mark.parametrize(
        "venue_factory", [offerers_factories.VenueFactory, offerers_factories.VenueWithoutSiretFactory]
    )
    def test_create_non_payment_notice_with_offerer_and_venue(self, authenticated_client, legit_user, venue_factory):
        offerer = offerers_factories.OffererFactory()
        venue = venue_factory(managingOfferer=offerer)
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
            html_parser.extract_alert(authenticated_client.get(response.location).data)
            == "L'avis d'impayé a été enregistré"
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

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.NON_PAYMENT_NOTICE_CREATED
        assert action.actionDate is not None
        assert action.authorUserId == legit_user.id
        assert action.offererId == offerer.id
        assert action.venueId == venue.id
        assert action.extraData == {"non_payment_notice_id": notice.id}

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


class GetEditFormTest(GetEndpointHelper):
    endpoint = "backoffice_web.non_payment_notices.get_edit_form"
    needed_permission = perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES
    endpoint_kwargs = {"notice_id": 1}
    expected_num_queries = 2  # session + notice

    def test_get_edit_form_test(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory()
        form_url = url_for(self.endpoint, notice_id=notice.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(form_url)
            assert response.status_code == 200

        assert html_parser.extract_input_value(response.data, "date_received") == notice.dateReceived.isoformat()
        assert html_parser.extract_select_options(response.data, "notice_type", True) == {
            offerers_models.NoticeType.UNPAID_AMOUNT_NOTICE.name: "Avis de sommes à payer"
        }
        assert html_parser.extract_input_value(response.data, "amount") == str(notice.amount)
        assert html_parser.extract_input_value(response.data, "reference") == notice.reference
        assert html_parser.extract_input_value(response.data, "emitter_name") == notice.emitterName
        assert html_parser.extract_input_value(response.data, "emitter_email") == notice.emitterEmail
        assert html_parser.extract_select_options(response.data, "offerer", True) == {}
        assert html_parser.extract_select_options(response.data, "venue", True) == {}

    def test_get_edit_form_test_with_offerer_and_venue(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        notice = offerers_factories.NonPaymentNoticeFactory(
            noticeType=offerers_models.NoticeType.REMINDER_LETTER,
            amount=Decimal("1500"),
            offerer=venue.managingOfferer,
            venue=venue,
        )
        form_url = url_for(self.endpoint, notice_id=notice.id)

        db.session.expire_all()

        with assert_num_queries(self.expected_num_queries + 2):  # queries on offerer and venue
            response = authenticated_client.get(form_url)
            assert response.status_code == 200

        assert html_parser.extract_input_value(response.data, "date_received") == notice.dateReceived.isoformat()
        assert html_parser.extract_select_options(response.data, "notice_type", True) == {
            offerers_models.NoticeType.REMINDER_LETTER.name: "Lettre de relance"
        }
        assert html_parser.extract_input_value(response.data, "amount") == str(notice.amount)
        assert html_parser.extract_input_value(response.data, "reference") == notice.reference
        assert html_parser.extract_input_value(response.data, "emitter_name") == notice.emitterName
        assert html_parser.extract_input_value(response.data, "emitter_email") == notice.emitterEmail
        assert html_parser.extract_tom_select_options(response.data, "offerer", True) == {
            str(
                venue.managingOfferer.id
            ): f"{venue.managingOfferer.id} - {venue.managingOfferer.name} ({venue.managingOfferer.siren})"
        }
        assert html_parser.extract_tom_select_options(response.data, "venue", True) == {
            str(venue.id): f"{venue.id} - {venue.common_name} ({venue.siret})"
        }


class EditTest(PostEndpointHelper):
    endpoint = "backoffice_web.non_payment_notices.edit"
    endpoint_kwargs = {"notice_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES

    def test_edit(self, authenticated_client):
        venue = offerers_factories.VenueFactory()
        notice = offerers_factories.NonPaymentNoticeFactory(offerer=venue.managingOfferer, venue=venue)

        new_date_received = datetime.date.today() - datetime.timedelta(days=3)

        response = self.post_to_endpoint(
            authenticated_client,
            notice_id=notice.id,
            form={
                "date_received": new_date_received.isoformat(),
                "notice_type": offerers_models.NoticeType.REMINDER_LETTER.name,
                "amount": "256.50",
                "reference": "NEWREF",
                "emitter_name": "Centre de recouvrement",
                "emitter_email": "recouvrement@example.com",
                "offerer": str(venue.managingOfferer.id),
                "venue": str(venue.id),
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        assert html_parser.extract_alert(response.data) == "L'avis d'impayé a été enregistré"

        db.session.refresh(notice)
        assert notice.dateReceived == new_date_received
        assert notice.status == offerers_models.NoticeStatus.CREATED
        assert notice.noticeType == offerers_models.NoticeType.REMINDER_LETTER
        assert notice.reference == "NEWREF"
        assert notice.emitterName == "Centre de recouvrement"
        assert notice.emitterEmail == "recouvrement@example.com"
        assert notice.amount == Decimal("256.50")
        assert notice.offerer == venue.managingOfferer
        assert notice.venue == venue
        assert notice.motivation is None
        assert notice.batch is None

        assert db.session.query(history_models.ActionHistory).count() == 0

    def test_edit_set_offerer_and_venue(self, authenticated_client, legit_user):
        venue = offerers_factories.VenueFactory()
        notice = offerers_factories.NonPaymentNoticeFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            notice_id=notice.id,
            form={
                "date_received": notice.dateReceived.isoformat(),
                "notice_type": notice.noticeType.name,
                "amount": str(notice.amount),
                "reference": notice.reference,
                "emitter_name": notice.emitterName,
                "emitter_email": notice.emitterEmail,
                "offerer": "",
                "venue": str(venue.id),
            },
            follow_redirects=True,
        )
        assert response.status_code == 200

        assert html_parser.extract_alert(response.data) == "L'avis d'impayé a été enregistré"

        db.session.refresh(notice)
        assert notice.offerer == venue.managingOfferer
        assert notice.venue == venue

        action = db.session.query(history_models.ActionHistory).one()
        assert action.actionType == history_models.ActionType.NON_PAYMENT_NOTICE_CREATED
        assert action.actionDate.date() == datetime.date.today()
        assert action.authorUserId == legit_user.id
        assert action.offererId == venue.managingOfferer.id
        assert action.venueId == venue.id
        assert action.extraData == {"non_payment_notice_id": notice.id}


class GetFormTestHelper(GetEndpointHelper):
    needed_permission = perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES
    endpoint_kwargs = {"notice_id": 1}
    expected_num_queries = 1  # session

    def test_get_form_test(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory()
        form_url = url_for(self.endpoint, notice_id=notice.id)

        with assert_num_queries(self.expected_num_queries):
            response = authenticated_client.get(form_url)
            assert response.status_code == 200


class GetSetPendingFormTest(GetFormTestHelper):
    endpoint = "backoffice_web.non_payment_notices.get_set_pending_form"


class SetPendingTest(PostEndpointHelper):
    endpoint = "backoffice_web.non_payment_notices.set_pending"
    endpoint_kwargs = {"notice_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES

    @pytest.mark.parametrize(
        "motivation, expected_template",
        [
            (
                offerers_models.NoticeStatusMotivation.OFFERER_NOT_FOUND,
                TransactionalEmail.NON_PAYMENT_NOTICE_PENDING_OFFERER_NOT_FOUND,
            ),
            (
                offerers_models.NoticeStatusMotivation.PRICE_NOT_FOUND,
                TransactionalEmail.NON_PAYMENT_NOTICE_PENDING_PRICE_NOT_FOUND,
            ),
        ],
    )
    def test_set_pending(self, authenticated_client, motivation, expected_template):
        notice = offerers_factories.NonPaymentNoticeFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            notice_id=notice.id,
            form={"motivation": motivation.name},
            follow_redirects=True,
        )
        assert response.status_code == 200

        html_parser.assert_no_alert(response.data)

        db.session.refresh(notice)
        assert notice.status == offerers_models.NoticeStatus.PENDING
        assert notice.motivation == motivation

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(expected_template.value)
        assert mails_testing.outbox[0]["To"] == notice.emitterEmail
        assert mails_testing.outbox[0]["params"] == {
            "AMOUNT": "199,99 €",
            "BATCH_LABEL": None,
            "DATE_RECEIVED": get_date_formatted_for_email(notice.dateReceived),
            "MOTIVATION": motivation.name,
            "OFFERER_NAME": None,
            "REFERENCE": notice.reference,
        }

    def test_set_missing_motivation(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            notice_id=notice.id,
            form={"motivation": ""},
            follow_redirects=True,
        )
        assert response.status_code == 200

        assert (
            html_parser.extract_alert(response.data)
            == "Les données envoyées comportent des erreurs. Motif : Information obligatoire ;"
        )

        db.session.refresh(notice)
        assert notice.status == offerers_models.NoticeStatus.CREATED
        assert len(mails_testing.outbox) == 0

    def test_set_excluded_motivation(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            notice_id=notice.id,
            form={"motivation": "ALREADY_PAID"},
            follow_redirects=True,
        )
        assert response.status_code == 200

        assert (
            html_parser.extract_alert(response.data)
            == "Les données envoyées comportent des erreurs. Motif : Not a valid choice. ;"
        )

        db.session.refresh(notice)
        assert notice.status == offerers_models.NoticeStatus.CREATED
        assert len(mails_testing.outbox) == 0


class GetNoContinuationFormTest(GetFormTestHelper):
    endpoint = "backoffice_web.non_payment_notices.get_set_no_continuation_form"


class SetNoContinuationTest(PostEndpointHelper):
    endpoint = "backoffice_web.non_payment_notices.set_no_continuation"
    endpoint_kwargs = {"notice_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES

    def test_set_no_continuation(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory()

        response = self.post_to_endpoint(authenticated_client, notice_id=notice.id, form={}, follow_redirects=True)
        assert response.status_code == 200

        html_parser.assert_no_alert(response.data)

        db.session.refresh(notice)
        assert notice.status == offerers_models.NoticeStatus.WITHOUT_CONTINUATION
        assert notice.motivation is None

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(
            TransactionalEmail.NON_PAYMENT_NOTICE_WITHOUT_CONTINUATION.value
        )
        assert mails_testing.outbox[0]["To"] == notice.emitterEmail
        assert mails_testing.outbox[0]["params"] == {
            "AMOUNT": "199,99 €",
            "BATCH_LABEL": None,
            "DATE_RECEIVED": get_date_formatted_for_email(notice.dateReceived),
            "MOTIVATION": None,
            "OFFERER_NAME": None,
            "REFERENCE": notice.reference,
        }


class GetCloseFormTest(GetFormTestHelper):
    endpoint = "backoffice_web.non_payment_notices.get_close_form"


class CloseTest(PostEndpointHelper):
    endpoint = "backoffice_web.non_payment_notices.close"
    endpoint_kwargs = {"notice_id": 1}
    needed_permission = perm_models.Permissions.MANAGE_NON_PAYMENT_NOTICES

    @pytest.mark.parametrize(
        "motivation, recipient_type, expected_template",
        [
            (
                offerers_models.NoticeStatusMotivation.ALREADY_PAID,
                offerers_models.NoticeRecipientType.PRO,
                TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED_TO_PRO,
            ),
            (
                offerers_models.NoticeStatusMotivation.REJECTED,
                offerers_models.NoticeRecipientType.PRO,
                TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED_TO_PRO,
            ),
            (
                offerers_models.NoticeStatusMotivation.NO_LINKED_BANK_ACCOUNT,
                offerers_models.NoticeRecipientType.PRO,
                TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED_TO_PRO,
            ),
            (
                offerers_models.NoticeStatusMotivation.ALREADY_PAID,
                offerers_models.NoticeRecipientType.SGC,
                TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED_TO_SGC_ALREADY_PAID,
            ),
            (
                offerers_models.NoticeStatusMotivation.REJECTED,
                offerers_models.NoticeRecipientType.SGC,
                TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED_TO_SGC_REJECTED,
            ),
            (
                offerers_models.NoticeStatusMotivation.NO_LINKED_BANK_ACCOUNT,
                offerers_models.NoticeRecipientType.SGC,
                TransactionalEmail.NON_PAYMENT_NOTICE_CLOSED_TO_SGC_NO_LINKED_BANK_ACCOUNT,
            ),
        ],
    )
    def test_terminate(self, authenticated_client, motivation, recipient_type, expected_template):
        offerer = offerers_factories.OffererFactory()
        batch = finance_factories.CashflowBatchFactory()
        notice = offerers_factories.NonPaymentNoticeFactory(
            amount=Decimal(1234.5), dateReceived=datetime.date(2025, 8, 7), offerer=offerer
        )
        response = self.post_to_endpoint(
            authenticated_client,
            notice_id=notice.id,
            form={"motivation": motivation.name, "recipient": recipient_type.name, "batch": batch.id},
            follow_redirects=True,
        )
        assert response.status_code == 200

        html_parser.assert_no_alert(response.data)

        db.session.refresh(notice)
        assert notice.status == offerers_models.NoticeStatus.CLOSED
        assert notice.motivation == motivation

        assert len(mails_testing.outbox) == 1
        assert mails_testing.outbox[0]["template"] == dataclasses.asdict(expected_template.value)
        assert mails_testing.outbox[0]["To"] == notice.emitterEmail
        assert mails_testing.outbox[0]["params"] == {
            "AMOUNT": "1234,50 €",
            "BATCH_LABEL": batch.label,
            "DATE_RECEIVED": "jeudi 7 août 2025",
            "MOTIVATION": motivation.name,
            "OFFERER_NAME": offerer.name,
            "REFERENCE": notice.reference,
        }

    def test_set_missing_fields(self, authenticated_client):
        notice = offerers_factories.NonPaymentNoticeFactory()

        response = self.post_to_endpoint(
            authenticated_client,
            notice_id=notice.id,
            form={"motivation": "", "recipient": "", "batch": ""},
            follow_redirects=True,
        )
        assert response.status_code == 200

        assert (
            html_parser.extract_alert(response.data) == "Les données envoyées comportent des erreurs. "
            "Motif : Information obligatoire ; "
            "Destinataire : Information obligatoire ; "
            "N° de virement : Information obligatoire ;"
        )

        db.session.refresh(notice)
        assert notice.status == offerers_models.NoticeStatus.CREATED
        assert len(mails_testing.outbox) == 0
