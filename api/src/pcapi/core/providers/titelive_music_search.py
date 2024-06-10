import logging
import typing

import pydantic.v1 as pydantic

from pcapi.connectors.serialization.titelive_serializers import GenreTitelive
from pcapi.connectors.serialization.titelive_serializers import TiteliveMusicArticle
from pcapi.connectors.serialization.titelive_serializers import TiteliveMusicWork
from pcapi.connectors.titelive import TiteliveBase
from pcapi.core.categories import subcategories_v2 as subcategories
from pcapi.core.offers import models as offers_models
from pcapi.domain import music_types

from .constants import MUSIC_SLUG_BY_GTL_ID
from .constants import NOT_CD_LIBELLES
from .constants import TITELIVE_MUSIC_SUPPORTS_BY_CODE
from .titelive_api import TiteliveSearch
from .titelive_api import activate_newly_eligible_product_and_offers


logger = logging.getLogger(__name__)


class CommonMusicArticleFields(typing.TypedDict):
    titre: str
    genre: GenreTitelive | None
    artiste: str | None
    label: str | None


class TiteliveMusicSearch(TiteliveSearch[TiteliveMusicWork]):
    titelive_base = TiteliveBase.MUSIC

    def deserialize_titelive_product(self, titelive_work: dict) -> TiteliveMusicWork:
        return pydantic.parse_obj_as(TiteliveMusicWork, titelive_work)

    def partition_allowed_products(
        self, titelive_product_page: list[TiteliveMusicWork]
    ) -> tuple[list[TiteliveMusicWork], list[str]]:
        non_allowed_eans = set()
        for work in titelive_product_page:
            article_ok = []
            for article in work.article:
                if is_music_codesupport_allowed(article.codesupport):
                    article_ok.append(article)
                else:
                    non_allowed_eans.add(article.gencod)
            work.article = article_ok

        return titelive_product_page, list(non_allowed_eans)

    def upsert_titelive_result_in_dict(
        self, titelive_search_result: TiteliveMusicWork, products_by_ean: dict[str, offers_models.Product]
    ) -> dict[str, offers_models.Product]:
        common_article_fields = get_common_article_fields(titelive_search_result)
        for article in titelive_search_result.article:
            ean = article.gencod
            product = products_by_ean.get(ean)
            if product is None:
                products_by_ean[ean] = self.create_product(article, common_article_fields)
            else:
                products_by_ean[ean] = self.update_product(article, common_article_fields, product)

        return products_by_ean

    def create_product(
        self, article: TiteliveMusicArticle, common_article_fields: CommonMusicArticleFields
    ) -> offers_models.Product:
        return offers_models.Product(
            description=article.resume,
            extraData=build_music_extra_data(article, common_article_fields),
            idAtProviders=article.gencod,
            lastProvider=self.provider,
            name=common_article_fields["titre"],
            subcategoryId=parse_titelive_music_codesupport(article.codesupport).id,
        )

    def update_product(
        self,
        article: TiteliveMusicArticle,
        common_article_fields: CommonMusicArticleFields,
        product: offers_models.Product,
    ) -> offers_models.Product:
        product.description = article.resume
        if product.extraData is None:
            product.extraData = offers_models.OfferExtraData()
        product.extraData.update(build_music_extra_data(article, common_article_fields))
        product.idAtProviders = article.gencod
        product.name = common_article_fields["titre"]
        product.subcategoryId = parse_titelive_music_codesupport(article.codesupport).id

        activate_newly_eligible_product_and_offers(product)

        return product


def get_common_article_fields(titelive_search_result: TiteliveMusicWork) -> CommonMusicArticleFields:
    titre = titelive_search_result.titre
    titelive_gtl = None
    artiste = None
    label = None
    for article in titelive_search_result.article:
        if titelive_gtl is None and article.gtl is not None:
            most_precise_genre = max(article.gtl.first.values(), key=lambda gtl: gtl.code)
            titelive_gtl = most_precise_genre

        if artiste is None and article.artiste is not None:
            artiste = article.artiste

        if label is None and article.label is not None:
            label = article.label

        if titelive_gtl is not None and artiste is not None and label is not None:
            break

    if titelive_gtl is None:
        logger.warning(
            "Genre not found for music %s, with EANs %s",
            titre,
            ", ".join(article.gencod for article in titelive_search_result.article),
        )
    if artiste is None:
        logger.warning(
            "Artist not found for music %s, with EANs %s",
            titre,
            ", ".join(article.gencod for article in titelive_search_result.article),
        )
    if label is None:
        logger.warning(
            "Label not found for music %s, with EANs %s",
            titre,
            ", ".join(article.gencod for article in titelive_search_result.article),
        )

    return CommonMusicArticleFields(titre=titre, genre=titelive_gtl, artiste=artiste, label=label)


def build_music_extra_data(
    article: TiteliveMusicArticle, common_article_fields: CommonMusicArticleFields
) -> offers_models.OfferExtraData:
    gtl_id = common_article_fields["genre"].code if common_article_fields["genre"] else None
    music_type, music_subtype = parse_titelive_music_genre(gtl_id)

    extra_data = offers_models.OfferExtraData(
        artist=common_article_fields["artiste"],
        author=article.compositeur,
        comment=article.commentaire,
        contenu_explicite=article.contenu_explicite,
        date_parution=article.dateparution.isoformat() if article.dateparution else None,
        dispo=article.dispo,
        distributeur=article.distributeur,
        ean=article.gencod,
        editeur=article.editeur,
        gtl_id=gtl_id,
        musicSubType=str(music_subtype.code),
        musicType=str(music_type.code),
        music_label=common_article_fields["label"],
        nb_galettes=article.nb_galettes,
        performer=article.interprete,
        prix_musique=str(article.prix) if article.prix is not None else None,
    )
    return typing.cast(
        offers_models.OfferExtraData, {key: value for key, value in extra_data.items() if value is not None}
    )


def parse_titelive_music_genre(gtl_id: str | None) -> tuple[music_types.MusicType, music_types.MusicSubType]:
    music_slug = (
        MUSIC_SLUG_BY_GTL_ID.get(gtl_id, music_types.OTHER_SHOW_TYPE_SLUG)
        if gtl_id
        else music_types.OTHER_SHOW_TYPE_SLUG
    )
    return (
        music_types.MUSIC_TYPES_BY_SLUG[music_slug],
        music_types.MUSIC_SUB_TYPES_BY_SLUG[music_slug],
    )


def is_music_codesupport_allowed(codesupport: str | None) -> bool:
    if not codesupport:
        return False

    support = TITELIVE_MUSIC_SUPPORTS_BY_CODE.get(codesupport)
    if support is None:
        logger.warning("received unexpected titelive codesupport %s", codesupport)
        return False

    return support["is_allowed"]


def parse_titelive_music_codesupport(codesupport: str | None) -> subcategories.Subcategory:
    assert codesupport, "empty code support was not filtered"

    support = TITELIVE_MUSIC_SUPPORTS_BY_CODE.get(codesupport)
    assert support, f"unexpected codesupport {codesupport} was not filtered"

    is_vinyl = any(not_cd_libelle in support["libelle"] for not_cd_libelle in NOT_CD_LIBELLES)
    if is_vinyl:
        return subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE
    return subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD
