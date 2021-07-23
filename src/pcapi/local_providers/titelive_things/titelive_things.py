from io import BytesIO
from io import TextIOWrapper
import logging
import re
from typing import Optional

from pcapi.connectors.ftp_titelive import connect_to_titelive_ftp
from pcapi.connectors.ftp_titelive import get_files_to_process_from_titelive_ftp
from pcapi.core.categories import subcategories
from pcapi.domain.titelive import get_date_from_filename
from pcapi.domain.titelive import read_things_date
from pcapi.local_providers.local_provider import LocalProvider
from pcapi.local_providers.providable_info import ProvidableInfo
from pcapi.models import BookFormat
from pcapi.models import Product
from pcapi.models.local_provider_event import LocalProviderEventType
from pcapi.repository import local_provider_event_queries
from pcapi.repository import product_queries
from pcapi.repository.product_queries import ProductWithBookingsException
from pcapi.utils.string_processing import trim_with_elipsis


logger = logging.getLogger(__name__)


DATE_REGEXP = re.compile(r"([a-zA-Z]+)(\d+).tit")
THINGS_FOLDER_NAME_TITELIVE = "livre3_11"
NUMBER_OF_ELEMENTS_PER_LINE = 46  # (45 elements from line + \n)
PAPER_PRESS_TVA = "2,10"
PAPER_PRESS_SUPPORT_CODE = "R"
UNRELEASED_BOOK_MARKER = "xxx"
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


class TiteLiveThings(LocalProvider):
    name = "TiteLive (Epagine / Place des libraires.com)"
    can_create = True

    def __init__(self):
        super().__init__()

        ordered_thing_files = get_files_to_process_from_titelive_ftp(THINGS_FOLDER_NAME_TITELIVE, DATE_REGEXP)
        self.thing_files = self.get_remaining_files_to_check(ordered_thing_files)

        self.data_lines = None
        self.products_file = None
        self.product_extra_data = {}

    def __next__(self) -> Optional[list[ProvidableInfo]]:
        if self.data_lines is None:
            self.open_next_file()

        try:
            data_lines = next(self.data_lines)
            elements = data_lines.split("~")
        except StopIteration:
            self.open_next_file()
            elements = next(self.data_lines).split("~")

        if len(elements) != NUMBER_OF_ELEMENTS_PER_LINE:
            self.log_provider_event(LocalProviderEventType.SyncError, "number of elements mismatch")
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
                product_queries.delete_unwanted_existing_product(book_unique_identifier)
            except ProductWithBookingsException:
                self.log_provider_event(
                    LocalProviderEventType.SyncError, f"Error deleting product with ISBN: {self.product_infos['ean13']}"
                )
            return []

        if is_unreleased_book(self.product_infos):
            logger.info(
                "Ignoring isbn=%s because it has 'xxx' in 'titre' and 'auteurs' fields, which means it is not yet released",
                book_unique_identifier,
            )
            return []

        book_information_last_update = read_things_date(self.product_infos["date_updated"])
        providable_info = self.create_providable_info(
            Product, book_unique_identifier, book_information_last_update, book_unique_identifier
        )
        return [providable_info]

    def get_ineligibility_reason(self) -> Optional[str]:
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

    def fill_object_attributes(self, product: Product):
        product.name = trim_with_elipsis(self.product_infos["titre"], 140)
        product.datePublished = read_things_date(self.product_infos["date_parution"])
        subcategory = subcategories.ALL_SUBCATEGORIES_DICT[self.product_subcategory_id]
        product.subcategoryId = subcategory.id
        product.type = subcategory.matching_type
        product.extraData = self.product_extra_data.copy()
        product.extraData.update(get_extra_data_from_infos(self.product_infos))

        if self.product_infos["url_extrait_pdf"] != "":
            if product.mediaUrls is None:
                product.mediaUrls = []

            product.mediaUrls.append(self.product_infos["url_extrait_pdf"])

    def open_next_file(self):
        if self.products_file:
            file_date = get_date_from_filename(self.products_file, DATE_REGEXP)
            self.log_provider_event(LocalProviderEventType.SyncPartEnd, file_date)
        self.products_file = next(self.thing_files)
        file_date = get_date_from_filename(self.products_file, DATE_REGEXP)
        self.log_provider_event(LocalProviderEventType.SyncPartStart, file_date)

        self.data_lines = get_lines_from_thing_file(str(self.products_file))

    def get_remaining_files_to_check(self, ordered_thing_files: list) -> iter:
        latest_sync_part_end_event = local_provider_event_queries.find_latest_sync_part_end_event(self.provider)
        if latest_sync_part_end_event is None:
            return iter(ordered_thing_files)
        for index, filename in enumerate(ordered_thing_files):
            if get_date_from_filename(filename, DATE_REGEXP) == int(latest_sync_part_end_event.payload):
                return iter(ordered_thing_files[index + 1 :])
        return iter([])


def get_lines_from_thing_file(thing_file: str):
    data_file = BytesIO()
    data_wrapper = TextIOWrapper(
        data_file,
        encoding="iso-8859-1",
        line_buffering=True,
    )
    file_path = "RETR " + THINGS_FOLDER_NAME_TITELIVE + "/" + thing_file
    connect_to_titelive_ftp().retrbinary(file_path, data_file.write)
    data_wrapper.seek(0, 0)
    return iter(data_wrapper.readlines())


def get_subcategory_and_extra_data_from_titelive_type(titelive_type):
    # pylint: disable=too-many-return-statements
    if titelive_type in ("A", "I", "LA"):  # obsolete codes
        return None, None
    if titelive_type == "BD":  # bande dessinée
        return subcategories.LIVRE_PAPIER.id, BookFormat.BANDE_DESSINEE.value
    if titelive_type == "BL":  # beaux livres
        return subcategories.LIVRE_PAPIER.id, BookFormat.BEAUX_LIVRES.value
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
        return subcategories.LIVRE_PAPIER.id, BookFormat.LIVRE_CASSETTE.value  # TODO: verify
    if titelive_type == "LD":  # livre + CD audio
        return subcategories.LIVRE_PAPIER.id, BookFormat.LIVRE_AUDIO.value  # TODO: verify
    if titelive_type == "LE":  # livre numérique
        return None, None
    if titelive_type == "LR":  # livre + CD-ROM
        return None, None
    if titelive_type == "LT":  # liseuses et tablettes
        return None, None
    if titelive_type == "LV":  # livre + DVD
        return None, None
    if titelive_type == "M":  # moyen format
        return subcategories.LIVRE_PAPIER.id, BookFormat.MOYEN_FORMAT.value
    if titelive_type == "O":  # objet
        return None, None
    if titelive_type == "P":  # poche
        return subcategories.LIVRE_PAPIER.id, BookFormat.POCHE.value
    if titelive_type == "PC":  # papeterie / consommable
        return None, None
    if titelive_type == "PS":  # poster
        return None, None
    if titelive_type == "R":  # revue
        return subcategories.LIVRE_PAPIER.id, BookFormat.REVUE.value  # TODO: verify
    if titelive_type in ("T", "TL"):  # livre papier (hors spécificité)
        return subcategories.LIVRE_PAPIER.id, None
    if titelive_type == "TR":  # transparents
        return None, None
    return None, None


def get_infos_from_data_line(elts: []) -> dict:
    infos = dict()
    infos["ean13"] = elts[0]
    infos["isbn"] = elts[1]
    infos["titre"] = elts[2]
    infos["titre_court"] = elts[3]
    infos["code_csr"] = elts[4]
    infos["code_dispo"] = elts[5]
    infos["collection"] = elts[6]
    infos["num_in_collection"] = elts[7]
    infos["prix"] = elts[9]
    infos["editeur"] = elts[10]
    infos["distributeur"] = elts[11]
    infos["date_parution"] = elts[12]
    infos["code_support"] = elts[13]
    infos["code_tva"] = elts[14]
    infos["n_pages"] = elts[15]
    infos["longueur"] = elts[16]
    infos["largeur"] = elts[17]
    infos["epaisseur"] = elts[18]
    infos["poids"] = elts[19]
    infos["is_update"] = elts[21]
    infos["auteurs"] = elts[23]
    infos["datetime_created"] = elts[24]
    infos["date_updated"] = elts[25]
    infos["taux_tva"] = elts[26]
    infos["libelle_csr"] = elts[27]
    infos["traducteur"] = elts[28]
    infos["langue_orig"] = elts[29]
    infos["commentaire"] = elts[31]
    infos["classement_top"] = elts[32]
    infos["has_image"] = elts[33]
    infos["code_edi_fournisseur"] = elts[34]
    infos["libelle_serie_bd"] = elts[35]
    infos["ref_editeur"] = elts[38]
    infos["is_scolaire"] = elts[39]
    infos["n_extraits_mp3"] = elts[40]
    infos["url_extrait_pdf"] = elts[41]
    infos["id_auteur"] = elts[42]
    infos["indice_dewey"] = elts[43]
    infos["code_regroupement"] = elts[44]
    return infos


def get_extra_data_from_infos(infos: dict) -> dict:
    extra_data = dict()
    extra_data["author"] = infos["auteurs"]
    extra_data["isbn"] = infos["ean13"]
    if infos["indice_dewey"] != "":
        extra_data["dewey"] = infos["indice_dewey"]
    extra_data["titelive_regroup"] = infos["code_regroupement"]
    extra_data["prix_livre"] = infos["prix"].replace(",", ".")
    extra_data["rayon"] = infos["libelle_csr"]
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
        extra_data["comment"] = trim_with_elipsis(infos["commentaire"], 92)
    return extra_data


def is_unreleased_book(product_info: dict) -> None:
    title = product_info.get("titre", "").lower()
    authors = product_info.get("auteurs", "").lower()
    return title == authors == UNRELEASED_BOOK_MARKER
