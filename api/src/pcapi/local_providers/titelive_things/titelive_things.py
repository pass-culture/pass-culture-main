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

INFO_KEYS = {
    "AUTEURS": "auteurs",
    "CLASSEMENT_TOP": "classement_top",
    "CODE_CLIL": "code_clil",
    "CODE_CSR": "code_csr",
    "CODE_DISPO": "code_dispo",
    "CODE_EDI_FOURNISSEUR": "code_edi_fournisseur",
    "CODE_REGROUPEMENT": "code_regroupement",
    "CODE_SUPPORT": "code_support",
    "CODE_TVA": "code_tva",
    "COLLECTION": "collection",
    "COMMENTAIRE": "commentaire",
    "DATE_PARUTION": "date_parution",
    "DATE_UPDATED": "date_updated",
    "DATETIME_CREATED": "datetime_created",
    "DISTRIBUTEUR": "distributeur",
    "EAN13": "ean13",
    "EDITEUR": "editeur",
    "EPAISSEUR": "epaisseur",
    "GTL_ID": "gtl_id",
    "HAS_IMAGE": "has_image",
    "INDICE_DEWEY": "indice_dewey",
    "IS_SCOLAIRE": "is_scolaire",
    "IS_UPDATE": "is_update",
    "LANGUE_ORIG": "langue_orig",
    "LARGEUR": "largeur",
    "LECTORAT_ID": "id_lectorat",
    "LONGUEUR": "longueur",
    "N_EXTRAITS_MP3": "n_extraits_mp3",
    "N_PAGES": "n_pages",
    "NUM_IN_COLLECTION": "num_in_collection",
    "POIDS": "poids",
    "PRIX": "prix",
    "TAUX_TVA": "taux_tva",
    "TITRE": "titre",
    "TRADUCTEUR": "traducteur",
}

OLD_FILTER_SCHOOL_RELATED_CSR_CODE = [
    "2700",
    "2701",
    "2702",
    "2703",
    "2704",
    "2800",
    "2801",
    "2802",
    "2803",
    "2804",
    "2900",
    "2901",
    "2902",
    "2903",
    "2904",
    "2905",
    "2906",
    "2907",
    "3000",
    "3001",
    "3002",
    "3003",
    "3004",
    "3005",
    "3006",
    "3007",
    "3008",
    "3302",
    "3303",
    "3304",
    "3511",
    "3611",
    "4001",
    "4002",
    "4800",
    "4803",
    "4806",
    "4807",
    "5512",
    "9620",
    "9621",
    "9622",
    "9623",
    "9800",
    "9811",
    "9812",
    "9814",
]


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
        ) = get_subcategory_and_extra_data_from_titelive_type(self.product_infos[INFO_KEYS["CODE_SUPPORT"]])
        book_unique_identifier = self.product_infos[INFO_KEYS["EAN13"]]

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

        book_information_last_update = read_things_date(self.product_infos[INFO_KEYS["DATE_UPDATED"]])
        providable_info = self.create_providable_info(
            offers_models.Product, book_unique_identifier, book_information_last_update, book_unique_identifier
        )
        logger.info(
            "Providable info %s with date_updated: %s",
            book_unique_identifier,
            self.product_infos[INFO_KEYS["DATE_UPDATED"]],
        )
        return [providable_info]

    def get_ineligibility_reason(self) -> str | None:
        gtl_id = self.product_infos[INFO_KEYS["GTL_ID"]].zfill(8)
        gtl_level_01_code = gtl_id[:2]
        gtl_level_02_code = gtl_id[2:4]
        title = self.product_infos.get(INFO_KEYS["TITRE"], "").lower()

        # Ouvrage avec pierres ou encens, jeux de société ou escape game en coffrets,
        # marchandisage : jouets, goodies, peluches, posters, papeterie, etc...
        if self.product_infos[INFO_KEYS["TAUX_TVA"]] == BASE_VAT:
            return "vat-20"

        # ouvrage du rayon scolaire
        if gtl_level_01_code == GTL_LEVEL_01_SCHOOL:
            return "school"

        # ouvrage du rayon parascolaire,
        # code de la route (méthode d'apprentissage + codes basiques), code nautique, code aviation, etc...
        if gtl_level_01_code == GTL_LEVEL_01_EXTRACURRICULAR:
            return "extracurricular"

        if self.product_infos[INFO_KEYS["CODE_SUPPORT"]] == CALENDAR_SUPPORT_CODE:
            return "calendar"

        if self.product_infos[INFO_KEYS["CODE_SUPPORT"]] == POSTER_SUPPORT_CODE:
            return "poster"

        if self.product_infos[INFO_KEYS["CODE_SUPPORT"]] == PAPER_CONSUMABLE_SUPPORT_CODE:
            return "paper-consumable"

        # Coffrets (contenant un produit + un petit livret)
        if self.product_infos[INFO_KEYS["CODE_SUPPORT"]] == BOX_SUPPORT_CODE:
            return "box"

        # Oracles contenant des jeux de tarot
        if self.product_infos[INFO_KEYS["CODE_SUPPORT"]] == OBJECT_SUPPORT_CODE:
            return "object"

        # ouvrage "lectorat 18+" (Pornographie / ultra-violence)
        if self.product_infos[INFO_KEYS["LECTORAT_ID"]] == LECTORAT_EIGHTEEN_ID:
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
            self.product_infos[INFO_KEYS["TAUX_TVA"]] == PAPER_PRESS_VAT
            and self.product_infos[INFO_KEYS["CODE_SUPPORT"]] == PAPER_PRESS_SUPPORT_CODE
        ):
            return "press"

        if not self.product_subcategory_id:
            return "uneligible-product-subcategory"

        return None

    def fill_object_attributes(self, product: offers_models.Product) -> None:
        product.name = trim_with_ellipsis(self.product_infos[INFO_KEYS["TITRE"]], 140)
        product.datePublished = parse_things_date_to_string(self.product_infos[INFO_KEYS["DATE_PARUTION"]])
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

    def get_remaining_files_to_check(self, ordered_thing_files: list) -> iter:  # type: ignore [valid-type]
        latest_sync_part_end_event = providers_repository.find_latest_sync_part_end_event(self.provider)
        if latest_sync_part_end_event is None:
            logger.info(
                "get_remaining_files_to_check: %s (ALL)",
                ",".join(ordered_thing_files),
            )
            return iter(ordered_thing_files)
        for index, filename in enumerate(ordered_thing_files):
            if get_date_from_filename(filename, DATE_REGEXP) == int(latest_sync_part_end_event.payload):  # type: ignore [arg-type]
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
    if titelive_type in ("A", "I", "LA"):  # obsolete codes
        return None, None
    if titelive_type == "BD":  # bande dessinée
        return subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.BANDE_DESSINEE.value
    if titelive_type == "BL":  # beaux livres
        return subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.BEAUX_LIVRES.value
    if titelive_type == "C":  # carte et plan
        return None, None
    if titelive_type == "CA":  # CD audio
        return None, None
    if titelive_type == BOX_SUPPORT_CODE:  # coffret / boite
        return None, None
    if titelive_type == "CD":  # CD-ROM
        return None, None
    if titelive_type == CALENDAR_SUPPORT_CODE:  # calendrier
        return None, None
    if titelive_type == "DV":  # DVD
        return None, None
    if titelive_type == "EB":  # contenu numérique (hors livre électronique)
        return None, None
    if titelive_type == "K7":  # cassette audio vidéo
        return None, None
    if titelive_type == "LA":  # obsolete code
        return None, None
    if titelive_type == "LC":  # livre + cassette
        return subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.LIVRE_CASSETTE.value  # TODO: verify
    if titelive_type == "LD":  # livre + CD audio
        return subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.LIVRE_AUDIO.value  # TODO: verify
    if titelive_type == "LE":  # livre numérique
        return None, None
    if titelive_type == "LR":  # livre + CD-ROM
        return None, None
    if titelive_type == "LT":  # liseuses et tablettes
        return None, None
    if titelive_type == "LV":  # livre + DVD
        return None, None
    if titelive_type == "M":  # moyen format
        return subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.MOYEN_FORMAT.value
    if titelive_type == OBJECT_SUPPORT_CODE:  # objet
        return None, None
    if titelive_type == "P":  # poche
        return subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.POCHE.value
    if titelive_type == PAPER_CONSUMABLE_SUPPORT_CODE:  # papeterie / consommable
        return None, None
    if titelive_type == POSTER_SUPPORT_CODE:  # poster
        return None, None
    if titelive_type == PAPER_PRESS_SUPPORT_CODE:  # revue
        return subcategories.LIVRE_PAPIER.id, providers_constants.BookFormat.REVUE.value  # TODO: verify
    if titelive_type in ("T", "TL"):  # livre papier (hors spécificité)
        return subcategories.LIVRE_PAPIER.id, None
    if titelive_type == "TR":  # transparents
        return None, None
    return None, None


def get_infos_from_data_line(elts: list) -> dict:
    infos = {}
    infos[INFO_KEYS["EAN13"]] = elts[COLUMN_INDICES["ean"]]
    infos[INFO_KEYS["TITRE"]] = elts[COLUMN_INDICES["titre"]]
    infos[INFO_KEYS["CODE_CSR"]] = elts[COLUMN_INDICES["code_rayon_csr"]]
    infos[INFO_KEYS["CODE_DISPO"]] = elts[COLUMN_INDICES["disponibilite"]]
    infos[INFO_KEYS["COLLECTION"]] = elts[COLUMN_INDICES["collection"]]
    infos[INFO_KEYS["NUM_IN_COLLECTION"]] = elts[COLUMN_INDICES["num_in_collection"]]
    infos[INFO_KEYS["PRIX"]] = elts[COLUMN_INDICES["prix_ttc"]]
    infos[INFO_KEYS["EDITEUR"]] = elts[COLUMN_INDICES["editeur"]]
    infos[INFO_KEYS["DISTRIBUTEUR"]] = elts[COLUMN_INDICES["distributeur"]]
    infos[INFO_KEYS["DATE_PARUTION"]] = elts[COLUMN_INDICES["date_commercialisation"]]
    infos[INFO_KEYS["CODE_SUPPORT"]] = elts[COLUMN_INDICES["code_support"]]
    infos[INFO_KEYS["CODE_TVA"]] = elts[COLUMN_INDICES["code_tva"]]
    infos[INFO_KEYS["N_PAGES"]] = elts[COLUMN_INDICES["nb_pages"]]
    infos[INFO_KEYS["LONGUEUR"]] = elts[COLUMN_INDICES["longueur"]]
    infos[INFO_KEYS["LARGEUR"]] = elts[COLUMN_INDICES["largeur"]]
    infos[INFO_KEYS["EPAISSEUR"]] = elts[COLUMN_INDICES["epaisseur"]]
    infos[INFO_KEYS["POIDS"]] = elts[COLUMN_INDICES["poids"]]
    infos[INFO_KEYS["IS_UPDATE"]] = elts[COLUMN_INDICES["statut_fiche"]]
    infos[INFO_KEYS["AUTEURS"]] = elts[COLUMN_INDICES["auteurs"]]
    infos[INFO_KEYS["DATETIME_CREATED"]] = elts[COLUMN_INDICES["date_creation"]]
    infos[INFO_KEYS["DATE_UPDATED"]] = elts[COLUMN_INDICES["date_derniere_maj"]]
    infos[INFO_KEYS["TAUX_TVA"]] = elts[COLUMN_INDICES["taux_tva"]]
    infos[INFO_KEYS["TRADUCTEUR"]] = elts[COLUMN_INDICES["traducteur"]]
    infos[INFO_KEYS["LANGUE_ORIG"]] = elts[COLUMN_INDICES["langue_vo"]]
    infos[INFO_KEYS["COMMENTAIRE"]] = elts[COLUMN_INDICES["commentaire"]]
    infos[INFO_KEYS["CLASSEMENT_TOP"]] = elts[COLUMN_INDICES["palmares_pro"]]
    infos[INFO_KEYS["HAS_IMAGE"]] = elts[COLUMN_INDICES["image"]]
    infos[INFO_KEYS["CODE_EDI_FOURNISSEUR"]] = elts[COLUMN_INDICES["fournisseur_edi"]]
    infos[INFO_KEYS["IS_SCOLAIRE"]] = elts[COLUMN_INDICES["scolaire"]]
    infos[INFO_KEYS["N_EXTRAITS_MP3"]] = elts[COLUMN_INDICES["compteur_mp3"]]
    infos[INFO_KEYS["INDICE_DEWEY"]] = elts[COLUMN_INDICES["indice_dewey"]]
    infos[INFO_KEYS["CODE_REGROUPEMENT"]] = elts[COLUMN_INDICES["code_regroupement"]]
    infos[INFO_KEYS["GTL_ID"]] = elts[COLUMN_INDICES["genre_tite_live"]]
    infos[INFO_KEYS["CODE_CLIL"]] = elts[COLUMN_INDICES["code_clil"]]
    infos[INFO_KEYS["LECTORAT_ID"]] = elts[COLUMN_INDICES["id_lectorat"]]
    return infos


def get_extra_data_from_infos(infos: dict) -> offers_models.OfferExtraData:
    extra_data = offers_models.OfferExtraData()
    extra_data["author"] = infos[INFO_KEYS["AUTEURS"]]
    extra_data["ean"] = infos[INFO_KEYS["EAN13"]]
    if infos[INFO_KEYS["GTL_ID"]]:
        csr_label = get_closest_csr(infos[INFO_KEYS["GTL_ID"]])
        extra_data["gtl_id"] = infos[INFO_KEYS["GTL_ID"]].zfill(8)
        if csr_label is not None:
            extra_data["rayon"] = csr_label.get("label")
            extra_data["csr_id"] = csr_label.get("csr_id")
    if infos[INFO_KEYS["CODE_CLIL"]]:
        extra_data["code_clil"] = infos[INFO_KEYS["CODE_CLIL"]]
    if infos[INFO_KEYS["INDICE_DEWEY"]] != "":
        extra_data["dewey"] = infos[INFO_KEYS["INDICE_DEWEY"]]
    extra_data["titelive_regroup"] = infos[INFO_KEYS["CODE_REGROUPEMENT"]]
    extra_data["prix_livre"] = infos[INFO_KEYS["PRIX"]].replace(",", ".")
    if infos[INFO_KEYS["IS_SCOLAIRE"]] == "1":
        extra_data["schoolbook"] = True
    if infos[INFO_KEYS["CLASSEMENT_TOP"]] != "":
        extra_data["top"] = infos[INFO_KEYS["CLASSEMENT_TOP"]]
    if infos[INFO_KEYS["COLLECTION"]] != "":
        extra_data["collection"] = infos[INFO_KEYS["COLLECTION"]]
    if infos[INFO_KEYS["NUM_IN_COLLECTION"]] != "":
        extra_data["num_in_collection"] = infos[INFO_KEYS["NUM_IN_COLLECTION"]]
    if infos[INFO_KEYS["COMMENTAIRE"]] != "":
        extra_data["comment"] = trim_with_ellipsis(infos[INFO_KEYS["COMMENTAIRE"]], 92)
    if infos[INFO_KEYS["EDITEUR"]] != "":
        extra_data["editeur"] = infos[INFO_KEYS["EDITEUR"]]
    if infos[INFO_KEYS["DATE_PARUTION"]] != "":
        extra_data["date_parution"] = infos[INFO_KEYS["DATE_PARUTION"]]
    if infos[INFO_KEYS["DISTRIBUTEUR"]] != "":
        extra_data["distributeur"] = infos[INFO_KEYS["DISTRIBUTEUR"]]
    return extra_data


def is_unreleased_book(product_infos: dict) -> bool:
    title = product_infos.get(INFO_KEYS["TITRE"], "").lower()
    authors = product_infos.get(INFO_KEYS["AUTEURS"], "").lower()
    return title == authors == offers_models.UNRELEASED_OR_UNAVAILABLE_BOOK_MARKER
