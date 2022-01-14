import logging
from typing import Optional

from pcapi.core.object_storage import BACKENDS_MAPPING
from pcapi.core.offers.models import Mediation
from pcapi.core.offers.models import Offer
from pcapi.core.users.models import Favorite
from pcapi.models import db
from pcapi.utils.human_ids import dehumanize
from pcapi.utils.human_ids import humanize


logger = logging.getLogger(__name__)
from pcapi.utils.module_loading import import_string


# OK
def _update_favorites_mediations(favorites: set, dry_run: bool = True) -> None:
    """
    This function will :
        - Update Favorites Mediations before deleting Mediations
    """
    logger.info("[_update_favorites_mediations()] START")
    total = len(favorites)
    count = 1
    for favorite in favorites:
        logger.info("Favorite %d / %d", count, total)
        current_mediation = favorite.mediation
        current_offer = current_mediation.offer
        offer_active_mediation = (
            Mediation.query.join(Offer)
            .filter(Offer.id == current_offer.id)
            .filter(Mediation.isActive.is_(True))
            .filter(Mediation.thumbCount > 0)
            .order_by(Mediation.dateCreated.desc())
        ).first()
        if offer_active_mediation is not None:
            favorite.mediation = offer_active_mediation
        else:
            favorite.mediation = None
        db.session.add(favorite)
        count += 1
    if dry_run:
        logger.info("rollback !!")
        db.session.rollback()
    else:
        logger.info("commit !!")
        db.session.commit()
    logger.info("[_update_favorites_mediations()] END")


# OK
def delete_obsolete_mediations(dry_run: bool = True) -> None:
    """
    This function will delete:
    - Mediations that are NOT active (the user deactivated it (for another or none))
    - Mediations that have a thumbCount of 0 (unexpected)
    This method will call the update_favorites_mediations with a set of favorites
    """
    if dry_run:
        logger.info("This a dry run; if you are sure about the changes, call this function with dry_run=False")

    db.session.commit()

    # Mediations which are inactives
    inactive_mediations_to_delete = Mediation.query.filter(Mediation.isActive.is_(False)).with_entities(Mediation.id)
    inactive_mediations_ids_to_delete = set(mediation_id for mediation_id, in inactive_mediations_to_delete.all())
    favorites_to_update = set(
        favorite
        for favorite in Favorite.query.filter(Favorite.mediationId.in_(inactive_mediations_ids_to_delete)).all()
    )
    _update_favorites_mediations(favorites_to_update, dry_run=dry_run)
    deleted_inactives = inactive_mediations_to_delete.delete()

    # Mediations with a thumbcount of 0 (unexpected)
    thumbless_mediations_to_delete = Mediation.query.filter(Mediation.thumbCount == 0).with_entities(Mediation.id)
    thumbless_mediations_ids_to_delete = set(mediation_id for mediation_id, in thumbless_mediations_to_delete.all())
    favorites_to_update = set(Favorite.query.filter(Favorite.mediationId.in_(thumbless_mediations_ids_to_delete)).all())
    _update_favorites_mediations(favorites_to_update, dry_run=dry_run)
    deleted_thumbless = thumbless_mediations_to_delete.delete()

    logger.info("%d inactive Mediations are about to be deleted", deleted_inactives)
    logger.info("%d Mediations without thumb are about to be deleted", deleted_thumbless)

    if dry_run:
        db.session.rollback()
    else:
        db.session.commit()

    inactive_count = Mediation.query.filter(Mediation.isActive.is_(False)).count()
    no_thumb_count = Mediation.query.filter(Mediation.thumbCount == 0).count()
    logger.info("There are now %d inactive Mediations", inactive_count)  # should be 0
    logger.info("There are now %d Mediations without thumb", no_thumb_count)  # should be 0


# OK
def delete_assets_tied_to_mediationsqlentities(
    backend_name: str = "local",
    dry_run: bool = True,
    container_name: Optional[str] = None,
    folder_name: str = "thumbs",
    marker: str = "thumbs/mediations",
    end_marker: str = "thumbs/mf",
    full_listing: bool = True,
) -> None:
    backend_path = BACKENDS_MAPPING[backend_name]
    if backend_name in ("OVH", "local"):
        backend = import_string(backend_path)
    else:
        raise ImportError("backend must be 'OVH' or 'local'")

    if dry_run:
        logger.info("This a dry run; if you are sure about the changes, call this function with dry_run=False")

    db.session.commit()

    old_mediationsqlentities_asset_names = set()

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

    # MediationSQLEntities assets
    logger.info(
        "%d assets that are related to a former MediationSQLEntity are about to be deleted",
        len(old_mediationsqlentities_asset_names),
    )
    if dry_run:
        pass
    else:
        for asset_name in old_mediationsqlentities_asset_names:
            logger.info("deleting asset: %s", asset_name)
            try:
                backend().delete_public_object(folder=folder_name, object_id=asset_name)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception("An unexpected error was encountered during deletion: %s", exc)


# OK
def delete_assets_without_mediation(
    backend_name: str = "local",
    dry_run: bool = True,
    container_name: Optional[str] = None,
    folder_name: str = "thumbs",
    marker: str = "thumbs/mediations",
    end_marker: str = "thumbs/mf",
    full_listing: bool = True,
) -> None:

    backend_path = BACKENDS_MAPPING[backend_name]
    if backend_name in ("OVH", "local"):
        backend = import_string(backend_path)
    else:
        raise ImportError("backend must be 'OVH' or 'local'")

    if dry_run:
        logger.info("This a dry run; if you are sure about the changes, call this function with dry_run=False")

    db.session.commit()

    current_mediation_asset_ids = set()
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

        if asset_name.startswith(f"{folder_name}/mediations/"):
            asset_name = asset_name.replace(f"{folder_name}/mediations/", "")
            if "_" in asset_name:
                continue
            mediation_id = dehumanize(asset_name)
            current_mediation_asset_ids.add(mediation_id)

    # create a set of Mediation IDs out of the list of tuples returned by the query
    current_mediation_ids = set((mediation_id for mediation_id, in Mediation.query.with_entities(Mediation.id).all()))

    # Assets without mediations
    orphan_asset_mediation_ids = current_mediation_asset_ids - current_mediation_ids
    orphan_assets_names = set()
    for numerical_id in orphan_asset_mediation_ids:
        human_id = humanize(numerical_id)
        orphan_assets_names.add(f"mediations/{human_id}")
    logger.info(
        "%d assets that are not related to a Mediation are about to be deleted",
        len(orphan_asset_mediation_ids),
    )
    if dry_run:
        pass
    else:
        for orphan_assets_name in orphan_assets_names:
            logger.info("deleting asset: %s", orphan_assets_name)
            try:
                backend().delete_public_object(folder=folder_name, object_id=orphan_assets_name)
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception("An unexpected error was encountered during deletion: %s", exc)


# EN COURS
def delete_mediations_without_uploaded_assets(
    backend_name: str = "local",
    dry_run: bool = True,
    container_name: Optional[str] = None,
    folder_name: str = "thumbs",
    marker: str = "thumbs/mediations",
    end_marker: str = "thumbs/mf",
    full_listing: bool = True,
) -> None:
    backend_path = BACKENDS_MAPPING[backend_name]
    if backend_name in ("OVH", "local"):
        backend = import_string(backend_path)
    else:
        raise ImportError("backend must be 'OVH' or 'local'")

    if dry_run:
        logger.info("This a dry run; if you are sure about the changes, call this function with dry_run=False")

    db.session.commit()
    current_mediation_asset_ids = set()
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

        if asset_name.startswith(f"{folder_name}/mediations/"):
            asset_name = asset_name.replace(f"{folder_name}/mediations/", "")
            if "_" in asset_name:
                continue
            try:
                mediation_id = dehumanize(asset_name)
            except Exception as exc:  # pylint: disable=broad-except
                logger.warning(exc)
            current_mediation_asset_ids.add(mediation_id)

    # create a set of Mediation IDs out of the list of tuples returned by the query
    current_mediation_ids = set((mediation_id for mediation_id, in Mediation.query.with_entities(Mediation.id).all()))

    # Mediations without assets
    orphan_mediation_ids = current_mediation_ids - current_mediation_asset_ids
    logger.info("There are %d Mediations without assets", len(orphan_mediation_ids))
    favorites_to_update = set(Favorite.query.filter(Favorite.mediationId.in_(orphan_mediation_ids)).all())
    _update_favorites_mediations(favorites_to_update)
    deleted_mediations_without_assets = Mediation.query.filter(Mediation.id.in_(orphan_mediation_ids)).delete(
        synchronize_session="fetch"
    )
    logger.info(
        "%d Mediations without assets are about to be deleted",
        deleted_mediations_without_assets,
    )
    if dry_run:
        db.session.rollback()
    else:
        db.session.commit()
