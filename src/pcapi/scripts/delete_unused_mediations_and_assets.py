from typing import Optional

from pcapi.core.object_storage import BACKENDS_MAPPING
from pcapi.core.offers.models import Mediation
from pcapi.models import db
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize
from pcapi.utils.logger import logger
from pcapi.utils.module_loading import import_string


def delete_obsolete_mediations(dry_run: bool = True) -> None:
    """
    This function will delete:
    - Mediations that are NOT active (the user replaced it with another one)
    - Mediations that have a thumbCount of 0 (unexpected)
    """
    if dry_run:
        logger.info("This a dry run; if you are sure about the changes, call this function with dry_run=False")

    db.session.commit()

    inactive_to_delete = Mediation.query.filter(Mediation.isActive.is_(False)).delete()
    no_thumb_to_delete = Mediation.query.filter(Mediation.thumbCount == 0).delete()
    logger.info("%d inactive Mediations are about to be deleted", inactive_to_delete)
    logger.info("%d Mediations without thumb are about to be deleted", no_thumb_to_delete)

    if dry_run:
        db.session.rollback()
    else:
        db.session.commit()

    inactive_count = Mediation.query.filter(Mediation.isActive.is_(False)).count()
    no_thumb_count = Mediation.query.filter(Mediation.thumbCount == 0).count()
    logger.info("There are now %d inactive Mediations", inactive_count)
    logger.info("There are now %d Mediations without thumb", no_thumb_count)


def delete_obsolete_thumbnails_in_object_storage(
    backend_name: str = "local",
    dry_run: bool = True,
    container_name: Optional[str] = None,
    folder_name: str = "thumbs",
    marker: str = "thumbs/mediations",
    end_marker: str = "thumbs/mf",
    full_listing: bool = True,
) -> None:
    """
    This function will collect all assets stored for a Mediation and the former model name MediationSQLEntity
    It will then compare the set to existing Mediations, and delete orphan assets ie for which no Mediation has the same ID
    It will also delete all assets tied to MediationSQLEntities
    It will also delete Mediation with several thumbs (and its assets)
    """
    backend_path = BACKENDS_MAPPING[backend_name]
    if backend_name in ("OVH", "local"):
        backend = import_string(backend_path)
    else:
        raise ImportError("backend must be 'OVH' or 'local'")

    if dry_run:
        logger.info("This a dry run; if you are sure about the changes, call this function with dry_run=False")

    db.session.commit()

    old_mediationsqlentities_asset_names = set()
    current_mediation_asset_ids = set()
    extra_thumb_asset_names = set()
    # get_container() returns a tuple of (dict of headers, list(dict of asset properties))
    mediation_assets = backend().get_container(
        container_name=container_name,
        marker=marker,
        end_marker=end_marker,
        full_listing=full_listing,
    )[1]

    for mediation_asset in mediation_assets:
        asset_name = mediation_asset["name"]

        if backend_name == "local" and asset_name.endswith(".type"):
            continue

        if asset_name.startswith(f"{folder_name}/mediationsqlentities/"):
            old_mediationsqlentities_asset_names.add(asset_name.replace(f"{folder_name}/", ""))

        if asset_name.startswith(f"{folder_name}/mediations/"):

            # Mediations should not have several thumbs
            if "_" in asset_name:
                extra_thumb_asset_names.add(asset_name.replace(f"{folder_name}/", ""))

            else:
                asset_name = asset_name.replace(f"{folder_name}/mediations/", "")
                mediation_id = dehumanize(asset_name)
                current_mediation_asset_ids.add(mediation_id)

    # create a set of Mediation IDs out of the list of tuples returned by the query
    current_mediation_ids = set((mediation_id for mediation_id, in Mediation.query.with_entities(Mediation.id).all()))

    # Mediations without assets
    orphan_mediation_ids = current_mediation_ids - current_mediation_asset_ids
    orphan_mediation_human_ids = {humanize(orphan_mediation_id) for orphan_mediation_id in orphan_mediation_ids}
    deleted_mediations_without_assets = Mediation.query.filter(Mediation.id.in_(orphan_mediation_ids)).delete(
        synchronize_session="fetch"
    )
    logger.info(
        "%d Mediations without assets are about to be deleted: IDs=%s aka humanized IDS=%s",
        deleted_mediations_without_assets,
        orphan_mediation_ids,
        orphan_mediation_human_ids,
    )
    if dry_run:
        db.session.rollback()
    else:
        db.session.commit()

    # Assets of extra thumbs
    logger.info(
        "%d assets that are not unique to a Mediation are about to be deleted",
        len(extra_thumb_asset_names),
    )
    if dry_run:
        pass
    else:
        for asset_name in extra_thumb_asset_names:
            print(f"deleting asset:{asset_name}")
            try:
                backend().delete_public_object(bucket=folder_name, object_id=asset_name)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception("An unexpected error was encountered during deletion: %s", exc)

    # Assets without mediations
    orphan_asset_mediation_ids = current_mediation_asset_ids - current_mediation_ids
    orphan_assets_names = set()
    for numerical_id in orphan_asset_mediation_ids:
        human_id = humanize(numerical_id)
        orphan_assets_names.add(f"mediations/{human_id}")
    logger.info(
        "%d assets that are not related to a Mediation are about to be deleted: %s",
        len(orphan_asset_mediation_ids),
        orphan_assets_names,
    )
    if dry_run:
        pass
    else:
        for orphan_assets_name in orphan_assets_names:
            print(f"deleting asset:{orphan_assets_name}")
            try:
                backend().delete_public_object(bucket=folder_name, object_id=orphan_assets_name)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception("An unexpected error was encountered during deletion: %s", exc)

    # MediationSQLEntities assets
    logger.info(
        "%d assets that are related to a former MediationSQLEntity are about to be deleted: %s",
        len(old_mediationsqlentities_asset_names),
        old_mediationsqlentities_asset_names,
    )
    if dry_run:
        pass
    else:
        for asset_name in old_mediationsqlentities_asset_names:
            print(f"deleting asset:{asset_name}")
            try:
                backend().delete_public_object(bucket=folder_name, object_id=asset_name)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception("An unexpected error was encountered during deletion: %s", exc)
