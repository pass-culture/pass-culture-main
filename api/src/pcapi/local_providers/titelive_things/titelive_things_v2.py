from io import BytesIO
from io import TextIOWrapper
import logging
import re

from pcapi.connectors.ftp_titelive import connect_to_titelive_ftp
from pcapi.connectors.ftp_titelive import get_files_to_process_from_titelive_ftp
from pcapi.core.categories import subcategories
import pcapi.core.offers.api as offers_api
from pcapi.core.offers.api import deactivate_permanently_unavailable_products
import pcapi.core.offers.exceptions as offers_exceptions
import pcapi.core.offers.models as offers_models
import pcapi.core.providers.models as providers_models
import pcapi.core.providers.repository as providers_repository
from pcapi.domain.titelive import get_date_from_filename
from pcapi.domain.titelive import read_things_date
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo


logger = logging.getLogger(__name__)


DATE_REGEXP = re.compile(r"([a-zA-Z]+)(\d+).tit")
THINGS_FOLDER_NAME_TITELIVE = "livre3_19"
THINGS_FOLDER_ENCODING_TITELIVE = "iso-8859-1"
NUMBER_OF_ELEMENTS_PER_LINE = 58  # (45 elements from line + \n)
PAPER_PRESS_TVA = "2,10"
COLUMN_INDICES = {
    "ean13": 0,
    # "isbn": 1,
    "titre": 1,
    # "titre_court": 3,
    "code_csr": 2,
    "code_dispo": 3,
    "collection": 4,
    "num_in_collection": 5,
    "prix": 6,
    "editeur": 7,
    "distributeur": 8,
    "date_parution": 9,
    "code_support": 10,
    "code_tva": 11,
    "n_pages": 12,
    "longueur": 13,
    "largeur": 14,
    "epaisseur": 15,
    "poids": 16,
    # "is_update": 21,
    "auteurs": 17,
    "datetime_created": 18,
    "date_updated": 19,
    "taux_tva": 20,
    # "libelle_csr": 27,
    "traducteur": 21,
    "is_scolaire": 27,
    "langue_orig": 29,
    "commentaire": 31,
    "classement_top": 32,
    "has_image": 33,
    "code_edi_fournisseur": 34,
    "libelle_serie_bd": 35,
    "ref_editeur": 38,
    "n_extraits_mp3": 40,
    "url_extrait_pdf": 41,
    "id_auteur": 42,
    "indice_dewey": 43,
    "code_regroupement": 44,
}
PAPER_PRESS_SUPPORT_CODE = "R"
SCHOOL_RELATED_CSR_CODE = [
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

    def __init__(self):  # type: ignore [no-untyped-def]
        super().__init__()

        ordered_thing_files = get_files_to_process_from_titelive_ftp(THINGS_FOLDER_NAME_TITELIVE, DATE_REGEXP)
        self.thing_files = self.get_remaining_files_to_check(ordered_thing_files)

        self.data_lines = None
        self.products_file = None
        self.product_extra_data = offers_models.OfferExtraData()

    def __next__(self) -> list[ProvidableInfo] | None:
        if self.data_lines is None:
            self.open_next_file()

        try:
            data_lines = next(self.data_lines)  # type: ignore [arg-type]
            elements = data_lines.split("~")
        except StopIteration:
            self.open_next_file()
            elements = next(self.data_lines).split("~")  # type: ignore [arg-type]

        if len(elements) != NUMBER_OF_ELEMENTS_PER_LINE:
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
            logger.info("Ignoring isbn=%s because reason=%s", book_unique_identifier, ineligibility_reason)
            try:
                offers_api.delete_unwanted_existing_product(book_unique_identifier)
            except offers_exceptions.CannotDeleteProductWithBookings:
                self.log_provider_event(
                    providers_models.LocalProviderEventType.SyncError,
                    f"Error deleting product with ISBN: {self.product_infos['ean13']}",
                )
            return []

        if is_unreleased_book(self.product_infos):
            products = offers_models.Product.query.filter(
                offers_models.Product.extraData["isbn"].astext == book_unique_identifier
            ).all()
            if len(products) > 0:
                deactivate_permanently_unavailable_products(book_unique_identifier)
                logger.info(
                    "deactivating products and offers with isbn=%s because it has 'xxx' in 'titre' and 'auteurs' fields, which means it is not yet released",
                    book_unique_identifier,
                )
            else:
                logger.info(
                    "Ignoring isbn=%s because it has 'xxx' in 'titre' and 'auteurs' fields, which means it is not yet released",
                    book_unique_identifier,
                )
            return []

        book_information_last_update = read_things_date(self.product_infos["date_updated"])
        providable_info = self.create_providable_info(
            offers_models.Product, book_unique_identifier, book_information_last_update, book_unique_identifier
        )
        return [providable_info]

    def get_ineligibility_reason(self) -> str | None:
        if self.product_infos["is_scolaire"] == "1" or self.product_infos["code_csr"] in SCHOOL_RELATED_CSR_CODE:
            return "school"

        if (
            self.product_infos["taux_tva"] == PAPER_PRESS_TVA
            and self.product_infos["code_support"] == PAPER_PRESS_SUPPORT_CODE
        ):
            return "press"

        if not self.product_subcategory_id:
            return "uneligible-product-subcategory"

        return None

    def fill_object_attributes(self, product: offers_models.Product) -> None:
        product.name = trim_with_ellipsis(self.product_infos["titre"], 140)
        product.datePublished = read_things_date(self.product_infos["date_parution"])
        if not self.product_subcategory_id:
            raise ValueError("product subcategory id is missing")
        subcategory = subcategories.ALL_SUBCATEGORIES_DICT[self.product_subcategory_id]
        product.subcategoryId = subcategory.id
        extra_data = self.product_extra_data | get_extra_data_from_infos(self.product_infos)
        product.extraData = extra_data
        #
        # if self.product_infos["url_extrait_pdf"] != "":
        #     if product.mediaUrls is None:
        #         product.mediaUrls = []
        #
        #     product.mediaUrls.append(self.product_infos["url_extrait_pdf"])

    def open_next_file(self):  # type: ignore [no-untyped-def]
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
            return iter(ordered_thing_files)
        for index, filename in enumerate(ordered_thing_files):
            if get_date_from_filename(filename, DATE_REGEXP) == int(latest_sync_part_end_event.payload):  # type: ignore [arg-type]
                return iter(ordered_thing_files[index + 1 :])
        return iter([])


def get_lines_from_thing_file(thing_file: str):  # type: ignore [no-untyped-def]
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
        return subcategories.LIVRE_PAPIER.id, offers_models.BookFormat.BANDE_DESSINEE.value
    if titelive_type == "BL":  # beaux livres
        return subcategories.LIVRE_PAPIER.id, offers_models.BookFormat.BEAUX_LIVRES.value
    if titelive_type == "C":  # carte et plan
        return None, None
    if titelive_type == "CA":  # CD audio
        return None, None
    if titelive_type == "CB":  # coffret / boite
        return None, None
    if titelive_type == "CD":  # CD-ROM
        return None, None
    if titelive_type == "CL":  # calendrier
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
        return subcategories.LIVRE_PAPIER.id, offers_models.BookFormat.LIVRE_CASSETTE.value  # TODO: verify
    if titelive_type == "LD":  # livre + CD audio
        return subcategories.LIVRE_PAPIER.id, offers_models.BookFormat.LIVRE_AUDIO.value  # TODO: verify
    if titelive_type == "LE":  # livre numérique
        return None, None
    if titelive_type == "LR":  # livre + CD-ROM
        return None, None
    if titelive_type == "LT":  # liseuses et tablettes
        return None, None
    if titelive_type == "LV":  # livre + DVD
        return None, None
    if titelive_type == "M":  # moyen format
        return subcategories.LIVRE_PAPIER.id, offers_models.BookFormat.MOYEN_FORMAT.value
    if titelive_type == "O":  # objet
        return None, None
    if titelive_type == "P":  # poche
        return subcategories.LIVRE_PAPIER.id, offers_models.BookFormat.POCHE.value
    if titelive_type == "PC":  # papeterie / consommable
        return None, None
    if titelive_type == "PS":  # poster
        return None, None
    if titelive_type == "R":  # revue
        return subcategories.LIVRE_PAPIER.id, offers_models.BookFormat.REVUE.value  # TODO: verify
    if titelive_type in ("T", "TL"):  # livre papier (hors spécificité)
        return subcategories.LIVRE_PAPIER.id, None
    if titelive_type == "TR":  # transparents
        return None, None
    return None, None


def get_infos_from_data_line(elts: list) -> dict:
    infos = {}
    for key, value in COLUMN_INDICES.items():
        infos[key] = elts[value]
    # infos["ean13"] = elts[0] # ISBN13
    # # infos["isbn"] = elts[1] # ISBN10  (absent v19)
    # infos["titre"] = elts[1] # titre
    # # infos["titre_court"] = elts[3] # titre court (absent v19)
    # infos["code_csr"] = elts[2] # code rayon CSR
    # infos["code_dispo"] = elts[3] # disponibilité
    # infos["collection"] = elts[4] # collection
    # infos["num_in_collection"] = elts[5] # Num collection
    # infos["prix"] = elts[6] # prix ttc
    # infos["editeur"] = elts[7] # editeur
    # infos["distributeur"] = elts[8] # distributeur
    # infos["date_parution"] = elts[9] # date commercialisation
    # infos["code_support"] = elts[10] # code support
    # infos["code_tva"] = elts[11] # code tva
    # infos["n_pages"] = elts[12] # nombre pages
    # infos["longueur"] = elts[13] # longueur (en cm)
    # infos["largeur"] = elts[14] # largeur (en cm)
    # infos["epaisseur"] = elts[15] # épaisseur (en cm)
    # infos["poids"] = elts[16] # poids (en g)
    # # infos["is_update"] = elts[21] # statut fiche (absent v19)
    # infos["auteurs"] = elts[17] # auteurs
    # infos["datetime_created"] = elts[18] # date création
    # infos["date_updated"] = elts[19] # date dernière maj
    # infos["taux_tva"] = elts[20] # taux tva
    # # infos["libelle_csr"] = elts[27] # libellé code rayon CSR (absent v19)
    # infos["traducteur"] = elts[21] # traducteur
    # infos["langue_orig"] = elts[22] # langue VO
    # infos["commentaire"] = elts[23] # commentaire
    # infos["classement_top"] = elts[24] # palmarès pro
    # infos["has_image"] = elts[25] # image
    # # infos["code_edi_fournisseur"] = elts[34] # code EDI fournisseur (absent v19)
    # infos["libelle_serie_bd"] = elts[26] # libellé série
    # # infos["ref_editeur"] = elts[38] # numéro de catalogue (absent v19)
    # infos["is_scolaire"] = elts[27] # scolaire
    # infos["n_extraits_mp3"] = elts[46] # compteur mp3
    # # infos["url_extrait_pdf"] = elts[41] # url feuilleteur (absent v19)
    # infos["id_auteur"] = elts[47] # id auteur
    # infos["indice_dewey"] = elts[28] # indice dewey
    # infos["code_regroupement"] = elts[29] # code regroupement
    return infos


def get_extra_data_from_infos(infos: dict) -> offers_models.OfferExtraData:
    extra_data = offers_models.OfferExtraData()
    extra_data["author"] = infos["auteurs"]
    extra_data["isbn"] = infos["ean13"]
    extra_data["ean"] = infos["ean13"]
    if infos["indice_dewey"] != "":
        extra_data["dewey"] = infos["indice_dewey"]
    extra_data["titelive_regroup"] = infos["code_regroupement"]
    extra_data["prix_livre"] = infos["prix"].replace(",", ".")
    # extra_data["rayon"] = infos["libelle_csr"]
    if infos["is_scolaire"] == "1":
        extra_data["schoolbook"] = True
    if infos["classement_top"] != "":
        extra_data["top"] = infos["classement_top"]
    if infos["collection"] != "":
        extra_data["collection"] = infos["collection"]
    if infos["num_in_collection"] != "":
        extra_data["num_in_collection"] = infos["num_in_collection"]
    if infos["libelle_serie_bd"] != "":
        extra_data["comic_series"] = infos["libelle_serie_bd"]
    if infos["commentaire"] != "":
        extra_data["comment"] = trim_with_ellipsis(infos["commentaire"], 92)
    if infos["editeur"] != "":
        extra_data["editeur"] = infos["editeur"]
    if infos["date_parution"] != "":
        extra_data["date_parution"] = infos["date_parution"]
    if infos["distributeur"] != "":
        extra_data["distributeur"] = infos["distributeur"]
    return extra_data


def is_unreleased_book(product_info: dict) -> bool:
    title = product_info.get("titre", "").lower()
    authors = product_info.get("auteurs", "").lower()
    return title == authors == offers_models.UNRELEASED_OR_UNAVAILABLE_BOOK_MARKER
