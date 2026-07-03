import logging
from itertools import cycle
from itertools import islice
from pathlib import Path
from shutil import copyfile

import pcapi.core.offers.factories as offers_factories
import pcapi.sandboxes
from pcapi import settings
from pcapi.connectors import thumb_storage
from pcapi.core.categories import subcategories
from pcapi.core.object_storage import delete_public_object_recursively
from pcapi.core.offers.models import Offer
from pcapi.models import db
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration
from pcapi.sandboxes.scripts.utils.select import remove_every
from pcapi.sandboxes.scripts.utils.storage_utils import read_sandbox_mediation_asset


logger = logging.getLogger(__name__)


OFFERS_WITH_MEDIATION_REMOVE_MODULO = 5


@log_func_duration
def prepare_mediations_folders() -> None:
    logger.info("prepare_mediations_folders")

    thumbs_folder_path = Path(pcapi.sandboxes.__path__[0]) / "thumbs"
    Path(thumbs_folder_path / "mediations").mkdir(parents=True, exist_ok=True)
    size = len(subcategories.ALL_SUBCATEGORIES)
    picture_filenames = [
        p.name for p in (thumbs_folder_path / "generic_pictures").iterdir() if not p.name.startswith(".")
    ]

    full_list = list(islice(cycle(picture_filenames), size))
    full_list.sort()

    for i in range(size):
        copyfile(
            thumbs_folder_path / "generic_pictures" / full_list[i],
            thumbs_folder_path / "mediations" / f"{subcategories.ALL_SUBCATEGORIES[i].id}.jpg",
        )


@log_func_duration
def create_industrial_mediations(offers_by_name: dict[str, Offer]) -> None:
    logger.info("create_industrial_mediations")

    mediations_by_name = {}

    offer_items = list(offers_by_name.items())
    offer_items_with_mediation = remove_every(offer_items, OFFERS_WITH_MEDIATION_REMOVE_MODULO)
    for offer_name, offer in offer_items_with_mediation:
        mediations_by_name[offer_name] = offers_factories.MediationFactory.create(offer=offer)

    db.session.add_all(mediations_by_name.values())
    db.session.commit()

    for mediation in mediations_by_name.values():
        image_as_bytes = read_sandbox_mediation_asset(mediation.offer.subcategoryId)
        thumb_storage.create_thumb(mediation, image_as_bytes, keep_ratio=True)

    db.session.add_all(mediations_by_name.values())
    db.session.commit()

    logger.info("created %d mediations", len(mediations_by_name))


def clean_industrial_mediations_bucket() -> None:
    logger.info("Cleaning thumbs bucket")
    delete_public_object_recursively(storage_path="thumbs", bucket=settings.GCP_BUCKET_NAME)
    logger.info("Thumbs bucket cleaned")
