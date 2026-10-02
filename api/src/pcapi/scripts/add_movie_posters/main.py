"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-43477/script_add_integration_movies \
  -f NAMESPACE=add_movie_posters \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
import os
import pathlib
import typing
from dataclasses import dataclass

import PIL
from pcapi.core.offers.exeptions import ImageValidationError

from pcapi.core.offers.api import create_movie_poster
from pcapi.core.offers.models import Product
from pcapi.core.providers.models import Provider
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


@dataclass
class MoviePoster:
    content: bytes
    product: Product


def fetch_provider(provider_id: int) -> Provider:
    return db.session.query(Provider).filter_by(id=provider_id).one()


def fetch_images() -> dict[int, bytes]:
    raw_images = {}
    namespace_dir = pathlib.Path(os.path.dirname(os.path.abspath(__file__)))
    images_dir = namespace_dir / "images"

    for name in os.listdir(images_dir):
        with open(images_dir / name, mode="rb") as f:
            try:
                allocine_id = int(name.split(".")[0])
            except Exception as error:
                logger.warning("File %s is unexpected. Error: %s", str(images_dir / name), str(error))
                raise

            raw_images[allocine_id] = f.read()

    return raw_images


def fetch_products(allocine_ids: typing.Collection[int]) -> typing.Collection[Product]:
    return db.session.query(Product).filter(Product.extraData.op("->")("allocineId").in_(allocine_ids))


def link_image_to_product(
    raw_images: dict[int, bytes], products: typing.Collection[Product]
) -> typing.Collection[MoviePoster]:
    movie_posters = []
    for product in products:
        allocine_id = product.extraData["allocineId"]
        movie_posters.append(MoviePoster(content=raw_images[allocine_id], product=product))
    return movie_posters


def main(provider_id: int) -> None:
    provider = fetch_provider(provider_id)
    raw_images = fetch_images()
    products = fetch_products(raw_images.keys())
    movie_posters = link_image_to_product(raw_images, products)

    movie_posters_added_count = 0
    for movie_poster in movie_posters:
        with atomic():
            try:
                create_movie_poster(movie_poster.product, provider, movie_poster.product)
            except (ImageValidationError, PIL.UnidentifiedImageError) as error:
                logger.warning(
                    "Failed to add movie poster to %d (allocine id: %d, bytes: %d). Cause: %s",
                    movie_poster.product.name,
                    movie_poster.product.extraData["allocineId"],
                    len(movie_poster.content),
                    str(error),
                )
            else:
                movie_posters_added_count += 1
                logger.info(
                    "Movie poster added to %s (allocine id: %d): %d bytes",
                    movie_poster.product.name,
                    movie_poster.product.extraData["allocineId"],
                    len(movie_poster.content),
                )

    if movie_posters_added_count == len(movie_posters):
        logger.info("Movie posters added: done. %d added.", len(movie_posters))
    else:
        logger.info(
            "Movie posters added: done with errors. %d/%d added.", len(movie_posters_added_count), len(movie_posters)
        )


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--provider-id", type=int)
    args = parser.parse_args()

    main(args.provider_id)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
