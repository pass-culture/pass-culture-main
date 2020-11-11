import os
from pathlib import Path
from unittest.mock import patch

import pytest

from pcapi.model_creators.generic_creators import create_booking
from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_product_with_thing_type
from pcapi.models import Offer
from pcapi.models import Product
from pcapi.repository import repository
from pcapi.scripts.remove_non_book_after_import import delete_product_from_isbn_file
from pcapi.scripts.remove_non_book_after_import import read_isbn_from_file


@pytest.mark.usefixtures("db_session")
@patch("pcapi.scripts.remove_non_book_after_import.read_isbn_from_file")
def test_remove_only_unwanted_book(read_isbn_from_file_mock, app):
    # Given
    unwanted_isbn = "9876543211231"
    conform_isbn = "0987654567098"
    product1 = create_product_with_thing_type(id_at_providers=unwanted_isbn)
    product2 = create_product_with_thing_type(id_at_providers=conform_isbn)

    read_isbn_from_file_mock.return_value = ["9876543211231", "1234567890981", "4567890987652", "0987467896549"]
    repository.save(product1, product2)

    # When
    delete_product_from_isbn_file("mon_fichier_isbns.txt")

    # Then
    assert Product.query.count() == 1


@pytest.mark.usefixtures("db_session")
@patch("pcapi.scripts.remove_non_book_after_import.read_isbn_from_file")
def test_should_not_delete_product_with_bookings_and_deactivate_associated_offer(read_isbn_from_file_mock, app):
    # Given
    unwanted_isbn = "9876543211231"
    product = create_product_with_thing_type(id_at_providers=unwanted_isbn)
    user = create_user()
    offerer = create_offerer(siren="775671464")
    venue = create_venue(offerer, name="Librairie Titelive", siret="77567146400110")
    offer = create_offer_with_thing_product(venue, product=product, is_active=True)
    stock = create_stock(offer=offer, price=0)
    booking = create_booking(user=user, stock=stock)
    repository.save(venue, product, offer, stock, booking, user)

    read_isbn_from_file_mock.return_value = ["9876543211231", "1234567890981", "4567890987652", "0987467896549"]
    repository.save(product)

    # When
    delete_product_from_isbn_file("mon_fichier_isbns.txt")

    # Then
    offer = Offer.query.one()
    assert offer.isActive is False
    assert Product.query.count() == 1


def test_read_isbn_from_file():
    # Given
    current_directory = Path(os.path.dirname(os.path.realpath(__file__)))
    file_path = f"{current_directory}/../files/isbn_test_file.txt"

    # When
    book_isbns = read_isbn_from_file(file_path)

    # Then
    assert len(book_isbns) == 2
    assert book_isbns[0] == "9876543211231"
    assert book_isbns[1] == "9876543211224"
