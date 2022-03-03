import base64
import io
import zipfile

from freezegun import freeze_time

from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalAttachment
from pcapi.core.mails.models.sendinblue_models import SendinblueTransactionalSender
from pcapi.utils.mailing import make_payment_details_email
from pcapi.utils.mailing import make_payment_message_email
from pcapi.utils.mailing import make_payments_report_email


@freeze_time("2018-10-15 09:21:34")
def test_make_payments_report_email(app):
    n_payments_by_status = {"NOT_PROCESSABLE": 1, "UNDER_REVIEW": 2}
    email = make_payments_report_email("csv1", n_payments_by_status)

    assert email["FromName"] == "pass Culture Pro"
    assert email["Subject"] == "Récapitulatif des paiements pass Culture Pro - 2018-10-15"
    assert "NOT_PROCESSABLE : 1" in email["Html-part"]
    assert "UNDER_REVIEW : 2" in email["Html-part"]
    assert "Nombre total de paiements : 3" in email["Html-part"]
    assert len(email["Attachments"]) == 1


@freeze_time("2018-10-15 09:21:34")
def test_make_payment_message_email(app):
    xml = '<?xml version="1.0" encoding="UTF-8"?><Document xmlns="urn:iso:std:iso:20022:tech:xsd:pain.001.001.03"></Document>'
    csv = "some csv"
    checksum = b"\x16\x91\x0c\x11~Hs\xc5\x1a\xa3W1\x13\xbf!jq@\xea  <h&\xef\x1f\xaf\xfc\x7fO\xc8\x82"

    email = make_payment_message_email(xml, csv, checksum)

    assert email.sender == SendinblueTransactionalSender.SUPPORT_PRO
    assert email.subject == "Virements XML pass Culture Pro - 2018-10-15"
    assert email.attachment == [
        SendinblueTransactionalAttachment(
            name="message_banque_de_france_20181015.xml",
            content="PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz48RG9j"
            "dW1lbnQgeG1sbnM9InVybjppc286c3RkOmlzbzoyMDAyMjp0ZWNoOnhz"
            "ZDpwYWluLjAwMS4wMDEuMDMiPjwvRG9jdW1lbnQ+",
        ),
        SendinblueTransactionalAttachment(name="lieux_20181015.csv", content="c29tZSBjc3Y="),
    ]

    assert "message_banque_de_france_20181015.xml" in email.html_content
    assert "16910c117e4873c51aa3573113bf216a7140ea20203c6826ef1faffc7f4fc882" in email.html_content


@freeze_time("2018-10-15 09:21:34")
def test_make_payment_details_email():
    # Given
    csv = '"header A","header B","header É"\n"part A","part B","part É"\n'

    # When
    email = make_payment_details_email(csv)

    # Then
    expected_csv_name = "details_des_paiements_20181015.csv"
    assert email["FromName"] == "pass Culture Pro"
    assert email["Subject"] == "Détails des paiements pass Culture Pro - 2018-10-15"
    assert email["Html-part"] == ""
    assert len(email["Attachments"]) == 1
    attachment = email["Attachments"][0]
    assert attachment["ContentType"] == "application/zip"
    assert attachment["Filename"] == f"{expected_csv_name}.zip"
    encoded_zip_content = attachment["Content"]
    zip_content = base64.b64decode(encoded_zip_content)
    with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
        assert zf.namelist() == [expected_csv_name]
        csv_in_zip_file = zf.open(expected_csv_name).read().decode("utf-8")
        assert csv_in_zip_file == csv
