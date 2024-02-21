""" 
Answer to the following warning :
We (borisLeBonPro and I, Lixxday) have done some checking
The result is available in the Notion page : https://www.notion.so/passcultureapp/Clean-les-eans-non-conformes-des-offres-et-produits-9ddde24dd57e467a9ab591e6da02dd4d#f1238d137f1a46e8a89aebcf01a1d926
We think it is safe to run this script, 
however part of the data will not be updated: 
- Non LIVRE_PAPIER with 10 numbers ean
- 13-chars eans with 10 numbers

WARNING : I (vencespass) personally think it is quite important
to have a look at the existing data before using this algorithm : 
I belive there are some easily fixable cases that could become lost after
this script is run.
Useful commands to check the data :
select * from product where "jsonData"->>'ean' is not null and (length("jsonData"->>'ean')>13);
select * from product where "jsonData"->>'ean' is not null and (length("jsonData"->>'ean')<13);
select * from product where "jsonData"->>'ean' is not null and length("jsonData"->>'ean')=13 and "jsonData"->>'ean' !~ '^[0-9]+$';
"""
from itertools import islice
import re
from typing import Generator

import sqlalchemy as sa

from pcapi.core.categories.subcategories_v2 import LIVRE_PAPIER
from pcapi.core.offers import models as offers_models
from pcapi.models import db


def print_and_write(file: str | None, message: str) -> None:
    print(message, file=open(file, "a", encoding="utf-8"))


def clean_product_or_offer(ean_object: offers_models.Product | offers_models.Offer, file: str | None = None) -> None:
    # Different types of ean to clean :
    # empty eans ({"ean":""})
    # Badly formatted eans ({"ean":"9-876543-2198-76"})
    # old eans, with length of 10 ({"ean":"2394739534"}) WARNING : sometimes, they have "-" too
    #   - Should add "978" at the beginning if subcategory is "Livre papier"

    # NOT HANDLED HERE:
    # i should use capslock eans ({"ean":"àéè-_'&éé"})
    # iDon'tKnowHowToUseAComputer ({"ean":"Author Name", "author"="9876543219876"})

    # --- --- ---

    # Log of what is done :
    #
    # NO_EAN, product_id (should not happen)
    #
    # Stuff to double check before committing:
    #   BAD_EAN, product_id, ean
    #   UPDATED_EAN, product_id, old_ean -> new_ean
    #   UPDATED_EAN_BOOK, product_id, old_ean -> new_ean
    #
    # Stuff for later:
    #   NOT_UPDATED_EAN_BOOK, product_id, subcategory, old_ean  -> new_ean (what we will need look at later)

    ean = ean_object.extraData.get("ean", None)
    if ean is None:
        print_and_write(file, f"NO_EAN, {ean_object.id}")
        return
    ean_numbers = [int(s) for s in re.findall(r"\d", ean)]
    new_ean = "".join([str(number) for number in ean_numbers])

    if len(new_ean) == 13:
        ean_object.extraData["ean"] = new_ean
        print_and_write(file, f"UPDATED_EAN, {ean_object.id}, {ean} -> {new_ean}")
    elif len(new_ean) == 10:
        if ean_object.subcategoryId == LIVRE_PAPIER.id:
            new_ean = "978" + new_ean
            ean_object.extraData["ean"] = new_ean
            print_and_write(file, f"UPDATED_EAN_BOOK, {ean_object.id}, {ean} -> {new_ean}")
        else:
            print_and_write(file, f"NOT_UPDATED_EAN_BOOK {ean_object.id}, {ean_object.subcategoryId}, {ean}")
    else:
        if ean != "":
            # We know what to do with empty eans, no need to log
            print_and_write(file, f"BAD_EAN {ean_object.id}, {ean}")
        ean_object.extraData.pop("ean", None)


def get_products(batch_size: int) -> Generator[offers_models.Product, None, None]:
    """Fetch products from database, without loading all of them at once."""
    try:
        for product in offers_models.Product.query.filter(
            sa.func.length(offers_models.Product.extraData["ean"].astext) != 13,
        ).yield_per(batch_size):
            yield product
    except Exception as err:
        print(f"Products fetch failed: {err}")
        raise
    print("All products fetched")


def get_products_chunks(
    chunk_size: int,
) -> Generator[list[offers_models.Product], None, None]:
    products = get_products(chunk_size)
    while True:
        chunk = list(islice(products, chunk_size))
        if chunk:
            yield chunk

        if len(chunk) < chunk_size:
            break


def get_offers(batch_size: int) -> Generator[offers_models.Offer, None, None]:
    """Fetch offers from database, without loading all of them at once."""
    try:
        for offer in offers_models.Offer.query.filter(
            sa.or_(
                sa.func.length(offers_models.Offer.extraData["ean"].astext) < 13,
                sa.func.length(offers_models.Offer.extraData["ean"].astext) > 13,
            )
        ).yield_per(batch_size):
            yield offer
    except Exception as err:
        print(f"Offers fetch failed: {err}")
        raise
    print("All offers fetched")


def get_offers_chunks(
    chunk_size: int,
) -> Generator[list[offers_models.Offer], None, None]:
    offers = get_offers(chunk_size)
    while True:
        chunk = list(islice(offers, chunk_size))
        if chunk:
            yield chunk

        if len(chunk) < chunk_size:
            break


def execute_clean_ean(dry_run=True):
    print("Starting update")
    chunk_size = 10000
    for chunk in get_products_chunks(chunk_size):
        for product in chunk:
            clean_product_or_offer(product, "result.txt")
    if dry_run:
        db.session.rollback()
        print("Rollback. Use dry_run = False if you want the script to commit.")
    else:
        db.session.commit()
        print("Commit. The script has been executed.")
    print("Update complete")
