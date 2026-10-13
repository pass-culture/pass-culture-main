import logging

from pcapi.core.categories import subcategories
from pcapi.core.discoveries import models as discoveries_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.sandboxes.scripts.utils.helpers import log_func_duration


logger = logging.getLogger(__name__)

MEDIA_TYPE_BY_SUBCATEGORY = {
    subcategories.LIVRE_PAPIER.id: discoveries_models.WorkMediaType.BOOK,
    subcategories.SEANCE_CINE.id: discoveries_models.WorkMediaType.FILM,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id: discoveries_models.WorkMediaType.MUSIC,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id: discoveries_models.WorkMediaType.MUSIC,
}


@log_func_duration
def create_industrial_works() -> None:
    logger.info("create_industrial_works")
    works_by_key = {(work.title, work.media_type): work for work in db.session.query(discoveries_models.Work).all()}
    products = (
        db.session.query(offers_models.Product)
        .filter(offers_models.Product.subcategoryId.in_(MEDIA_TYPE_BY_SUBCATEGORY))
        .order_by(offers_models.Product.id)
        .all()
    )

    for product in products:
        media_type = MEDIA_TYPE_BY_SUBCATEGORY[product.subcategoryId]
        key = (product.name, media_type)
        work = product.work or works_by_key.get(key)
        if work is None:
            work = discoveries_models.Work(title=product.name, media_type=media_type)
            db.session.add(work)
            works_by_key[key] = work
        product.work = work

        linked_artist_ids = {link.artist_id for link in work.artist_links}
        for artist_link in product.artistLinks:
            if artist_link.artist_id not in linked_artist_ids:
                db.session.add(
                    discoveries_models.WorkArtist(
                        work=work,
                        artist=artist_link.artist,
                        role=artist_link.artist_type.value if artist_link.artist_type else "contributor",
                    )
                )
                linked_artist_ids.add(artist_link.artist_id)

    db.session.commit()
    logger.info("created works for %d products", len(products))
