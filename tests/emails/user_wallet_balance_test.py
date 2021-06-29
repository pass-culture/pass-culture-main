import base64
import io
import zipfile

from freezegun import freeze_time

from pcapi.utils.mailing import make_wallet_balances_email


@freeze_time("2018-10-15 09:21:34")
def test_make_wallet_balances_email():
    # Given
    csv = '"header A","header B","header C","header D"\n"part A","part B","part C","part D"\n'

    # When
    email = make_wallet_balances_email(csv)

    # Then
    assert email["FromName"] == "pass Culture Pro"
    assert email["Subject"] == "Soldes des utilisateurs pass Culture - 2018-10-15"
    assert email["Html-part"] == ""
    assert len(email["Attachments"]) == 1
    assert email["Attachments"][0]["ContentType"] == "application/zip"
    expected_csv_name = "soldes_des_utilisateurs_20181015.csv"
    assert email["Attachments"][0]["Filename"] == f"{expected_csv_name}.zip"
    zip_content = base64.b64decode(email["Attachments"][0]["Content"])
    with zipfile.ZipFile(io.BytesIO(zip_content)) as zf:
        assert zf.namelist() == [expected_csv_name]
        csv_in_zip_file = zf.open(expected_csv_name).read().decode("utf-8")
        assert csv_in_zip_file == csv
