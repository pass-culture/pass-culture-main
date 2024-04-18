from io import BytesIO
from io import TextIOWrapper
import logging
import re
from typing import Iterator

from pcapi.connectors.ftp_titelive import connect_to_titelive_ftp
from pcapi.connectors.ftp_titelive import get_files_to_process_from_titelive_ftp
from pcapi.core.categories import subcategories_v2 as subcategories
import pcapi.core.fraud.models as fraud_models
import pcapi.core.offers.api as offers_api
from pcapi.core.offers.api import deactivate_permanently_unavailable_products
from pcapi.core.offers.exceptions import NotUpdateProductOrOffers
from pcapi.core.offers.exceptions import ProductNotFound
import pcapi.core.offers.models as offers_models
from pcapi.core.providers import constants as providers_constants
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.domain.titelive import get_date_from_filename
from pcapi.domain.titelive import parse_things_date_to_string
from pcapi.domain.titelive import read_things_date
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.utils.csr import get_closest_csr


logger = logging.getLogger(__name__)


DATE_REGEXP = re.compile(r"([a-zA-Z]+)(\d+).tit")
THINGS_FOLDER_NAME_TITELIVE = "livre3_19"
THINGS_FOLDER_ENCODING_TITELIVE = "iso-8859-1"
NUMBER_OF_ELEMENTS_PER_LINE = 63  # (62 elements from line + \n)

PAPER_PRESS_VAT = "2,10"
BASE_VAT = "20,00"

GTL_LEVEL_01_SCHOOL = "11"
GTL_LEVEL_01_EXTRACURRICULAR = "12"
GTL_LEVEL_01_YOUNG = "02"
GTL_LEVEL_02_BEFORE_3 = "02"
GTL_LEVEL_02_AFTER_3_AND_BEFORE_6 = "03"

LECTORAT_EIGHTEEN_ID = "45"

TOEIC_TEXT = "toeic"
TOEFL_TEXT = "toefl"

PAPER_PRESS_SUPPORT_CODE = "R"
BOX_SUPPORT_CODE = "CB"
OBJECT_SUPPORT_CODE = "O"
CALENDAR_SUPPORT_CODE = "CL"
PAPER_CONSUMABLE_SUPPORT_CODE = "PC"
POSTER_SUPPORT_CODE = "PS"

COLUMN_INDICES = {
    "ean": 0,
    "titre": 1,
    "code_rayon_csr": 2,
    "disponibilite": 3,
    "collection": 4,
    "num_in_collection": 5,
    "prix_ttc": 6,
    "editeur": 7,
    "distributeur": 8,
    "date_commercialisation": 9,
    "code_support": 10,
    "code_tva": 11,
    "nb_pages": 12,
    "longueur": 13,
    "largeur": 14,
    "epaisseur": 15,
    "poids": 16,
    "auteurs": 17,
    "date_creation": 18,
    "date_derniere_maj": 19,
    "taux_tva": 20,
    "traducteur": 21,
    "langue_vo": 22,
    "commentaire": 23,
    "palmares_pro": 24,
    "image": 25,
    "libelle_serie": 26,
    "scolaire": 27,
    "indice_dewey": 28,
    "code_regroupement": 29,
    "pure_numerique": 30,
    "livre_etranger": 31,
    "presence_presentation": 32,
    "prix_litteraire": 33,
    "presence_biographie": 34,
    "image_4eme_de_couverture": 35,
    "id_langue": 36,
    "numerique": 37,
    "compteur_pages_interieurs": 38,
    "pdf_extrait": 39,
    "pdf_premier_chapitre": 40,
    "pdf_paragraphe": 41,
    "liste_goodies": 42,
    "impression_a_la_demande": 43,
    "nouveau_code_langue": 44,
    "id_lectorat": 45,
    "compteur_mp3": 46,
    "id_auteurs": 47,
    "fonctions_auteurs": 48,
    "livre_lu": 49,
    "grands_caractères": 50,
    "multilingue": 51,
    "illustre": 52,
    "luxe": 53,
    "relie": 54,
    "broche": 55,
    "lu_par": 56,
    "genre_tite_live": 57,
    "code_clil": 58,
    "fournisseur_edi": 59,
    "statut_fiche": 60,
    "code_media_base": 61,
}


def trim_with_ellipsis(string: str, length: int) -> str:
    length_wo_ellipsis = length - 1
    return string[:length_wo_ellipsis] + (string[length_wo_ellipsis:] and "…")


class TiteLiveThings(LocalProvider):
    name = "TiteLive (Epagine / Place des libraires.com)"
    can_create = True

    def __init__(self) -> None:
        super().__init__()

        ordered_thing_files = get_files_to_process_from_titelive_ftp(THINGS_FOLDER_NAME_TITELIVE, DATE_REGEXP)
        self.thing_files = self.get_remaining_files_to_check(ordered_thing_files)

        self.data_lines: Iterator[str] | None = None
        self.products_file = None
        self.product_approved_eans: list[str | None] = []
        self.product_updated_ids: list[int] = []
        self.product_extra_data = offers_models.OfferExtraData()
        self.product_whitelist_eans = {
            ean for ean, in fraud_models.ProductWhitelist.query.with_entities(fraud_models.ProductWhitelist.ean).all()
        }

    def __next__(self) -> list[ProvidableInfo] | None:
        if self.data_lines is None:
            self.open_next_file()

        assert self.data_lines is not None
        try:
            data_lines = next(self.data_lines)
            elements = data_lines.split("~")
        except StopIteration:
            self.open_next_file()
            elements = next(self.data_lines).split("~")

        if len(elements) != NUMBER_OF_ELEMENTS_PER_LINE:
            logger.error(
                "SyncError: number of elements mismatch. (expected: %s, actual: %s)",
                NUMBER_OF_ELEMENTS_PER_LINE,
                len(elements),
            )
            self.log_provider_event(providers_models.LocalProviderEventType.SyncError, "number of elements mismatch")
            return []

        self.product_infos = get_infos_from_data_line(elements)

        (
            self.product_subcategory_id,
            self.product_extra_data["bookFormat"],
        ) = get_subcategory_and_extra_data_from_titelive_type(self.product_infos["code_support"])
        book_unique_identifier = self.product_infos["ean13"]

        ineligibility_reason = self.get_ineligibility_reason()

        if ineligibility_reason:
            if book_unique_identifier in self.product_whitelist_eans:
                logger.info(
                    "Allowing ean=%s even if ineligible reason=%s as it is a whitelisted product",
                    book_unique_identifier,
                    ineligibility_reason,
                )
            else:
                offers_api.reject_inappropriate_products([book_unique_identifier], None)
                logger.info(
                    "Rejecting ineligible ean=%s because reason=%s", book_unique_identifier, ineligibility_reason
                )
                return []

        if is_unreleased_book(self.product_infos):
            products = offers_models.Product.query.filter(
                offers_models.Product.extraData["ean"].astext == book_unique_identifier
            ).all()
            if len(products) > 0:
                deactivate_permanently_unavailable_products(book_unique_identifier)
                logger.info(
                    "deactivating products and offers with ean=%s because it has 'xxx' in 'titre' and 'auteurs' fields, which means it is not yet released",
                    book_unique_identifier,
                )
            else:
                logger.info(
                    "Ignoring ean=%s because it has 'xxx' in 'titre' and 'auteurs' fields, which means it is not yet released",
                    book_unique_identifier,
                )
            return []

        book_information_last_update = read_things_date(self.product_infos["date_updated"])
        providable_info = self.create_providable_info(
            offers_models.Product, book_unique_identifier, book_information_last_update, book_unique_identifier
        )
        logger.info(
            "Providable info %s with date_updated: %s",
            book_unique_identifier,
            self.product_infos["date_updated"],
        )
        return [providable_info]

    def get_ineligibility_reason(self) -> str | None:
        gtl_id = self.product_infos["gtl_id"].zfill(8)
        gtl_level_01_code = gtl_id[:2]
        gtl_level_02_code = gtl_id[2:4]
        title = self.product_infos.get("titre", "").lower()

        # Ouvrage avec pierres ou encens, jeux de société ou escape game en coffrets,
        # marchandisage : jouets, goodies, peluches, posters, papeterie, etc...
        if self.product_infos["taux_tva"] == BASE_VAT:
            return "vat-20"

        # ouvrage du rayon scolaire
        if gtl_level_01_code == GTL_LEVEL_01_SCHOOL:
            return "school"

        # ouvrage du rayon parascolaire,
        # code de la route (méthode d'apprentissage + codes basiques), code nautique, code aviation, etc...
        if gtl_level_01_code == GTL_LEVEL_01_EXTRACURRICULAR:
            return "extracurricular"

        if self.product_infos["code_support"] == CALENDAR_SUPPORT_CODE:
            return "calendar"

        if self.product_infos["code_support"] == POSTER_SUPPORT_CODE:
            return "poster"

        if self.product_infos["code_support"] == PAPER_CONSUMABLE_SUPPORT_CODE:
            return "paper-consumable"

        # Coffrets (contenant un produit + un petit livret)
        if self.product_infos["code_support"] == BOX_SUPPORT_CODE:
            return "box"

        # Oracles contenant des jeux de tarot
        if self.product_infos["code_support"] == OBJECT_SUPPORT_CODE:
            return "object"

        # ouvrage "lectorat 18+" (Pornographie / ultra-violence)
        if self.product_infos["id_lectorat"] == LECTORAT_EIGHTEEN_ID:
            return "pornography-or-violence"

        # Petite jeunesse (livres pour le bains, peluches, puzzles, etc...)
        if gtl_level_01_code == GTL_LEVEL_01_YOUNG and gtl_level_02_code in [
            GTL_LEVEL_02_BEFORE_3,
            GTL_LEVEL_02_AFTER_3_AND_BEFORE_6,
        ]:
            return "small-young"

        # Toeic or toefl
        if TOEIC_TEXT in title or TOEFL_TEXT in title:
            return "toeic-toefl"

        if (
            self.product_infos["taux_tva"] == PAPER_PRESS_VAT
            and self.product_infos["code_support"] == PAPER_PRESS_SUPPORT_CODE
        ):
            return "press"

        if not self.product_subcategory_id:
            return "uneligible-product-subcategory"

        return None

    def fill_object_attributes(self, product: offers_models.Product) -> None:
        product.name = trim_with_ellipsis(self.product_infos["titre"], 140)
        product.datePublished = parse_things_date_to_string(self.product_infos["date_parution"])
        if not self.product_subcategory_id:
            raise ValueError("product subcategory id is missing")
        subcategory = subcategories.ALL_SUBCATEGORIES_DICT[self.product_subcategory_id]
        product.subcategoryId = subcategory.id
        extra_data = self.product_extra_data | get_extra_data_from_infos(self.product_infos)
        product.extraData = extra_data

        if (
            product.gcuCompatibilityType == offers_models.GcuCompatibilityType.PROVIDER_INCOMPATIBLE
            and product.extraData
        ):
            self.product_approved_eans.append(product.extraData.get("ean"))

        if product.extraData and product.id is not None:
            self.product_updated_ids.append(product.id)

    def open_next_file(self) -> None:
        if self.products_file:
            file_date = get_date_from_filename(self.products_file, DATE_REGEXP)
            self.log_provider_event(providers_models.LocalProviderEventType.SyncPartEnd, file_date)
        self.products_file = next(self.thing_files)
        file_date = get_date_from_filename(self.products_file, DATE_REGEXP)
        self.log_provider_event(providers_models.LocalProviderEventType.SyncPartStart, file_date)

        self.data_lines = get_lines_from_thing_file(str(self.products_file))

    def get_remaining_files_to_check(self, ordered_thing_files: list) -> iter:  # type: ignore[valid-type]
        latest_sync_part_end_event = providers_repository.find_latest_sync_part_end_event(self.provider)
        if latest_sync_part_end_event is None:
            logger.info(
                "get_remaining_files_to_check: %s (ALL)",
                ",".join(ordered_thing_files),
            )
            return iter(ordered_thing_files)
        for index, filename in enumerate(ordered_thing_files):
            if get_date_from_filename(filename, DATE_REGEXP) == int(latest_sync_part_end_event.payload):  # type: ignore[arg-type]
                ordered_thing_files_from_date = ordered_thing_files[index + 1 :]
                logger.info(
                    "get_remaining_files_to_check: %s",
                    ",".join(ordered_thing_files_from_date),
                )
                return iter(ordered_thing_files_from_date)
        return iter([])

    def postTreatment(self) -> None:
        # If the product is updated to eligible, it is because the offers must be approved to become ineligible due to gcu
        for ean in self.product_approved_eans:
            try:
                if ean is None:
                    raise ProductNotFound("ean is None")
                offers_api.approves_provider_product_and_rejected_offers(ean)
            except ProductNotFound as exception:
                logger.error("Imported product with ean not found", extra={"ean": ean, "exc": str(exception)})
            except NotUpdateProductOrOffers as exception:
                logger.error("Product with ean cannot be approved", extra={"ean": ean, "exc": str(exception)})

        for product_id in self.product_updated_ids:
            try:
                offers_api.fill_offer_extra_data_from_product_data(product_id)
            except ProductNotFound as exception:
                logger.error("Imported product not found", extra={"product_id": product_id, "exc": str(exception)})
            except NotUpdateProductOrOffers as exception:
                logger.error("Offers cannot be updated", extra={"product_id": product_id, "exc": str(exception)})


def get_lines_from_thing_file(thing_file: str) -> Iterator[str]:
    data_file = BytesIO()
    data_wrapper = TextIOWrapper(
        data_file,
        encoding=THINGS_FOLDER_ENCODING_TITELIVE,
        line_buffering=True,
    )
    file_path = "RETR " + THINGS_FOLDER_NAME_TITELIVE + "/" + thing_file
    connect_to_titelive_ftp().retrbinary(file_path, data_file.write)
    data_wrapper.seek(0, 0)
    return iter(data_wrapper.readlines())


def get_subcategory_and_extra_data_from_titelive_type(titelive_type: str) -> tuple[str | None, str | None]:
    empty = (None, None)
    d = {
        "A": empty,  # obsolete code
        "BD": (subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.BANDE_DESSINEE.value),  # bande dessinée
        "BL": (subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.BEAUX_LIVRES.value),  # beaux livres
        "C": empty,  # carte et plan
        "CA": empty,  # CD audio
        BOX_SUPPORT_CODE: empty,  # coffret / boite
        "CD": empty,  # CD-ROM
        CALENDAR_SUPPORT_CODE: empty,  # calendrier
        "DV": empty,  # DVD
        "EB": empty,  # contenu numérique (hors livre électronique)
        "I": empty,  # obsolete code
        "K7": empty,  # cassette audio vidéo
        "LA": empty,  # obsolete code
        # TODO: verify:
        "LC": (subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.LIVRE_CASSETTE.value),  # livre + cassette
        # TODO: verify:
        "LD": (subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.LIVRE_AUDIO.value),  # livre + CD audio
        "LE": empty,  # livre numérique
        "LR": empty,  # livre + CD-ROM
        "LT": empty,  # liseuses et tablettes
        "LV": empty,  # livre + DVD
        "M": (subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.MOYEN_FORMAT.value),  # moyen format
        OBJECT_SUPPORT_CODE: empty,  # objet
        "P": (subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.POCHE.value),  # poche
        PAPER_CONSUMABLE_SUPPORT_CODE: empty,  # papeterie / consommable
        POSTER_SUPPORT_CODE: empty,  # poster
        # TODO: verify:
        PAPER_PRESS_SUPPORT_CODE: (subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.REVUE.value),  # revue
        "T": (subcategories.LIVRE_PAPIER.id, None),  # livre papier (hors spécificité)
        "TL": (subcategories.LIVRE_PAPIER.id, None),  # livre papier (hors spécificité)
        "TR": empty,  # transparents
    }
    return d.get(titelive_type, empty)


def get_infos_from_data_line(elts: list) -> dict:
    infos = {
        "ean13": elts[COLUMN_INDICES["ean"]],
        "titre": elts[COLUMN_INDICES["titre"]],
        "code_csr": elts[COLUMN_INDICES["code_rayon_csr"]],
        "code_dispo": elts[COLUMN_INDICES["disponibilite"]],
        "collection": elts[COLUMN_INDICES["collection"]],
        "num_in_collection": elts[COLUMN_INDICES["num_in_collection"]],
        "prix": elts[COLUMN_INDICES["prix_ttc"]],
        "editeur": elts[COLUMN_INDICES["editeur"]],
        "distributeur": elts[COLUMN_INDICES["distributeur"]],
        "date_parution": elts[COLUMN_INDICES["date_commercialisation"]],
        "code_support": elts[COLUMN_INDICES["code_support"]],
        "code_tva": elts[COLUMN_INDICES["code_tva"]],
        "n_pages": elts[COLUMN_INDICES["nb_pages"]],
        "longueur": elts[COLUMN_INDICES["longueur"]],
        "largeur": elts[COLUMN_INDICES["largeur"]],
        "epaisseur": elts[COLUMN_INDICES["epaisseur"]],
        "poids": elts[COLUMN_INDICES["poids"]],
        "is_update": elts[COLUMN_INDICES["statut_fiche"]],
        "auteurs": elts[COLUMN_INDICES["auteurs"]],
        "datetime_created": elts[COLUMN_INDICES["date_creation"]],
        "date_updated": elts[COLUMN_INDICES["date_derniere_maj"]],
        "taux_tva": elts[COLUMN_INDICES["taux_tva"]],
        "traducteur": elts[COLUMN_INDICES["traducteur"]],
        "langue_orig": elts[COLUMN_INDICES["langue_vo"]],
        "commentaire": elts[COLUMN_INDICES["commentaire"]],
        "classement_top": elts[COLUMN_INDICES["palmares_pro"]],
        "has_image": elts[COLUMN_INDICES["image"]],
        "code_edi_fournisseur": elts[COLUMN_INDICES["fournisseur_edi"]],
        "is_scolaire": elts[COLUMN_INDICES["scolaire"]],
        "n_extraits_mp3": elts[COLUMN_INDICES["compteur_mp3"]],
        "indice_dewey": elts[COLUMN_INDICES["indice_dewey"]],
        "code_regroupement": elts[COLUMN_INDICES["code_regroupement"]],
        "gtl_id": elts[COLUMN_INDICES["genre_tite_live"]],
        "code_clil": elts[COLUMN_INDICES["code_clil"]],
        "id_lectorat": elts[COLUMN_INDICES["id_lectorat"]],
    }
    return infos


def get_extra_data_from_infos(infos: dict) -> offers_models.OfferExtraData:
    extra_data = offers_models.OfferExtraData()
    extra_data["author"] = infos["auteurs"]
    extra_data["ean"] = infos["ean13"]
    if infos["gtl_id"]:
        csr_label = get_closest_csr(infos["gtl_id"])
        extra_data["gtl_id"] = infos["gtl_id"].zfill(8)
        if csr_label is not None:
            extra_data["rayon"] = csr_label.get("label")
            extra_data["csr_id"] = csr_label.get("csr_id")
    if infos["code_clil"]:
        extra_data["code_clil"] = infos["code_clil"]
    if infos["indice_dewey"] != "":
        extra_data["dewey"] = infos["indice_dewey"]
    extra_data["titelive_regroup"] = infos["code_regroupement"]
    extra_data["prix_livre"] = infos["prix"].replace(",", ".")
    if infos["is_scolaire"] == "1":
        extra_data["schoolbook"] = True
    if infos["classement_top"] != "":
        extra_data["top"] = infos["classement_top"]
    if infos["collection"] != "":
        extra_data["collection"] = infos["collection"]
    if infos["num_in_collection"] != "":
        extra_data["num_in_collection"] = infos["num_in_collection"]
    if infos["commentaire"] != "":
        extra_data["comment"] = trim_with_ellipsis(infos["commentaire"], 92)
    if infos["editeur"] != "":
        extra_data["editeur"] = infos["editeur"]
    if infos["date_parution"] != "":
        extra_data["date_parution"] = infos["date_parution"]
    if infos["distributeur"] != "":
        extra_data["distributeur"] = infos["distributeur"]
    return extra_data


def is_unreleased_book(product_infos: dict) -> bool:
    title = product_infos.get("titre", "").lower()
    authors = product_infos.get("auteurs", "").lower()
    return title == authors == offers_models.UNRELEASED_OR_UNAVAILABLE_BOOK_MARKER
