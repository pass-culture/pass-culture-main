from unittest.mock import patch

from freezegun import freeze_time

from pcapi.utils.mailing import make_wallet_balances_email


@patch('pcapi.utils.mailing.SUPPORT_EMAIL_ADDRESS', 'support@example.com')
@freeze_time('2018-10-15 09:21:34')
def test_make_wallet_balances_email():
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'

    # When
    email = make_wallet_balances_email(csv)

    # Then
    csv_binary = 'ImhlYWRlciBBIiwiaGVhZGVyIEIiLCJoZWFkZXIgQyIsImhlYWRlciBEIgoicGFydCBBIiwicGFydCBCIiwicGFydCBDIiwicGFydCBEIgo='
    assert email["FromEmail"] == 'support@example.com'
    assert email["FromName"] == "pass Culture Pro"
    assert email["Subject"] == "Soldes des utilisateurs pass Culture - 2018-10-15"
    assert email["Html-part"] == ""
    assert email["Attachments"] == [{"ContentType": "text/csv",
                                     "Filename": "soldes_des_utilisateurs_20181015.csv",
                                     "Content": csv_binary}]
