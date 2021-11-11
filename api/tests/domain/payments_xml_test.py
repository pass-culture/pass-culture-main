import datetime
from io import BytesIO

from freezegun import freeze_time
from lxml import etree
from lxml.etree import DocumentInvalid
import pytest

import pcapi.core.offers.factories as offers_factories
import pcapi.core.payments.factories as payments_factories
from pcapi.domain.payments import generate_message_file
from pcapi.domain.payments import validate_message_file_structure
from pcapi.models.payment import Payment


XML_NAMESPACE = {"ns": "urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"}


@pytest.mark.usefixtures("db_session")
class GenerateMessageFileTest:
    def test_basics(self):
        iban1, bic1 = "CF13QSDFGH456789", "QSDFGH8Z555"
        batch_date = datetime.datetime.now()
        offerer1 = offers_factories.OffererFactory(siren="siren1")
        p1 = payments_factories.PaymentFactory(
            batchDate=batch_date,
            amount=10,
            iban=iban1,
            bic=bic1,
            transactionLabel="remboursement 1ère quinzaine 09-2018",
            recipientName="first offerer",
            booking__stock__offer__venue__managingOfferer=offerer1,
        )
        offerer2 = offers_factories.OffererFactory(siren="siren2")
        iban2, bic2 = "FR14WXCVBN123456", "WXCVBN7B444"
        p2 = payments_factories.PaymentFactory(
            batchDate=batch_date,
            amount=20,
            iban=iban2,
            bic=bic2,
            recipientName="second offerer",
            transactionLabel="remboursement 1ère quinzaine 09-2018",
            booking__stock__offer__venue__managingOfferer=offerer2,
        )
        payments_factories.PaymentFactory(
            batchDate=batch_date,
            amount=40,
            iban=iban2,
            bic=bic2,
            recipientName="second offerer",
            transactionLabel="remboursement 1ère quinzaine 09-2018",
            booking__stock__offer__venue__managingOfferer=offerer2,
        )

        recipient_iban = "BD12AZERTY123456"
        recipient_bic = "AZERTY9Q666"
        message_id = "passCulture-SCT-20181015-114356"
        remittance_code = "remittance-code"
        with freeze_time("2018-10-15 09:21:34"):
            xml = generate_message_file(
                Payment.query, batch_date, recipient_iban, recipient_bic, message_id, remittance_code
            )

        # Group header
        assert (
            find_node("//ns:GrpHdr/ns:MsgId", xml) == message_id
        ), 'The message id should look like "passCulture-SCT-YYYYMMDD-HHMMSS"'
        assert (
            find_node("//ns:GrpHdr/ns:CreDtTm", xml) == "2018-10-15T09:21:34"
        ), 'The creation datetime should look like YYYY-MM-DDTHH:MM:SS"'
        assert (
            find_node("//ns:GrpHdr/ns:InitgPty/ns:Nm", xml) == "pass Culture"
        ), 'The initiating party should be "pass Culture"'
        assert (
            find_node("//ns:GrpHdr/ns:CtrlSum", xml) == "70.00"
        ), "The control sum should match the total amount of money to pay"
        assert (
            find_node("//ns:GrpHdr/ns:NbOfTxs", xml) == "2"
        ), "The number of transactions should match the distinct number of IBANs"

        # Payment info
        assert (
            find_node("//ns:PmtInf/ns:PmtInfId", xml) == message_id
        ), "The payment info id should be the same as message id since we only send one payment per XML message"
        assert (
            find_node("//ns:PmtInf/ns:NbOfTxs", xml) == "2"
        ), "The number of transactions should match the distinct number of IBANs"
        assert (
            find_node("//ns:PmtInf/ns:CtrlSum", xml) == "70.00"
        ), "The control sum should match the total amount of money to pay"
        assert (
            find_node("//ns:PmtInf/ns:PmtMtd", xml) == "TRF"
        ), "The payment method should be TRF because we want to transfer money"
        assert find_node("//ns:PmtInf/ns:PmtTpInf/ns:SvcLvl/ns:Cd", xml) == "SEPA"
        assert (
            find_node("//ns:PmtInf/ns:PmtTpInf/ns:CtgyPurp/ns:Cd", xml) == "GOVT"
        ), "The category purpose should be GOVT since we handle government subventions"
        assert find_node("//ns:PmtInf/ns:DbtrAgt/ns:FinInstnId/ns:BIC", xml) == recipient_bic
        assert find_node("//ns:PmtInf/ns:DbtrAcct/ns:Id/ns:IBAN", xml) == recipient_iban
        assert (
            find_node("//ns:PmtInf/ns:Dbtr/ns:Nm", xml) == "pass Culture"
        ), 'The name of the debtor should be "pass Culture"'
        assert (
            find_node("//ns:PmtInf/ns:ReqdExctnDt", xml) == "2018-10-22"
        ), "The requested execution datetime should be in one week from now"
        assert (
            find_node("//ns:PmtInf/ns:ChrgBr", xml) == "SLEV"
        ), 'The charge bearer should be SLEV as in "following service level"'
        assert (
            find_node("//ns:PmtInf/ns:CdtTrfTxInf/ns:UltmtDbtr/ns:Nm", xml) == "pass Culture"
        ), 'The ultimate debtor name should be "pass Culture"'
        assert find_node("//ns:InitgPty/ns:Id/ns:OrgId/ns:Othr/ns:Id", xml) == remittance_code

        # Transaction-specific content
        ibans = find_all_nodes("//ns:PmtInf/ns:CdtTrfTxInf/ns:CdtrAcct/ns:Id/ns:IBAN", xml)
        assert ibans == [iban1, iban2]
        bics = find_all_nodes("//ns:PmtInf/ns:CdtTrfTxInf/ns:CdtrAgt/ns:FinInstnId/ns:BIC", xml)
        assert bics == [bic1, bic2]
        names = find_all_nodes("//ns:PmtInf/ns:CdtTrfTxInf/ns:Cdtr/ns:Nm", xml)
        assert names == ["first offerer", "second offerer"]
        sirens = find_all_nodes("//ns:PmtInf/ns:CdtTrfTxInf/ns:Cdtr/ns:Id/ns:OrgId/ns:Othr/ns:Id", xml)
        assert sirens == ["siren1", "siren2"]
        labels = find_all_nodes("//ns:PmtInf/ns:CdtTrfTxInf/ns:RmtInf/ns:Ustrd", xml)
        assert labels == list(("remboursement 1ère quinzaine 09-2018",) * 2)
        amounts = find_all_nodes("//ns:PmtInf/ns:CdtTrfTxInf/ns:Amt/ns:InstdAmt", xml)
        assert amounts == ["10.00", "60.00"]
        e2e_ids = find_all_nodes("//ns:PmtInf/ns:CdtTrfTxInf/ns:PmtId/ns:EndToEndId", xml)
        assert e2e_ids == [p1.transactionEndToEndId.hex, p2.transactionEndToEndId.hex]

        # Finally, make sure that the file is valid
        validate_message_file_structure(xml)


def test_validate_message_file_structure_raises_on_error(app):
    # given
    transaction_file = """
        <broken><xml></xml></broken>
    """

    # when
    with pytest.raises(DocumentInvalid) as e:
        validate_message_file_structure(transaction_file)

    # then
    assert str(e.value) == "Element 'broken': No matching global declaration available for the validation root., line 2"


def find_node(xpath, transaction_file):
    xml = BytesIO(transaction_file.encode())
    tree = etree.parse(xml, etree.XMLParser())
    node = tree.find(xpath, namespaces=XML_NAMESPACE)
    return node.text


def find_all_nodes(xpath, transaction_file):
    xml = BytesIO(transaction_file.encode())
    tree = etree.parse(xml, etree.XMLParser())
    nodes = tree.findall(xpath, namespaces=XML_NAMESPACE)
    return [node.text for node in nodes]
