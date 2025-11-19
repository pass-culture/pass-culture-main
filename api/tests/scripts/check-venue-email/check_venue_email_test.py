# import logging
# import os

# import pytest

# from pcapi.core.offerers.factories import VenueFactory
# from pcapi.scripts.check_venue_email.main import main


# @pytest.mark.usefixtures("db_session")
# def test_check_email(caplog):
#     # Create venues with valid and invalid emails
#     VenueFactory(bookingEmail="email@example.com")
#     VenueFactory(bookingEmail="")  # Empty email is considered valid
#     invalid_venue_1 = VenueFactory(bookingEmail="invalid-email")
#     invalid_venue_2 = VenueFactory(bookingEmail="another-invalid-email@.com")

#     with caplog.at_level(logging.INFO):
#         main()

#     # Check that the log contains the expected invalid emails
#     assert "Total invalid emails: 2" in caplog.text
#     assert "{}, invalid-email".format(invalid_venue_1.id) in caplog.text
#     assert "{}, another-invalid-email@.com".format(invalid_venue_2.id) in caplog.text

#     # find CSV output
#     output_file = f"{os.environ['OUTPUT_DIRECTORY']}/venues_with_invalid_emails.csv"
#     with open(output_file, "r", encoding="utf-8") as csvfile:
#         content = csvfile.read()
#         assert '"venue_id";"booking_email"' in content
#         assert f'{invalid_venue_1.id};"invalid-email"' in content
#         assert f'{invalid_venue_2.id};"another-invalid-email@.com"' in content
