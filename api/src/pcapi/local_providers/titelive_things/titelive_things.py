from io import BytesIO
from io import TextIOWrapper
import logging
import re

from pcapi.connectors.ftp_titelive import connect_to_titelive_ftp
from pcapi.connectors.ftp_titelive import get_files_to_process_from_titelive_ftp
from pcapi.core.categories import subcategories
import pcapi.core.fraud.models as fraud_models
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
THINGS_FOLDER_NAME_TITELIVE = "livre3_11"
NUMBER_OF_ELEMENTS_PER_LINE = 46  # (45 elements from line + \n)
PAPER_PRESS_TVA = "2,10"
COLUMN_INDICES = (
    {  #  this list all field as per in the v11 documentation provided by titelive, without renaming fields.
        "ean": 0,
        "isbn": 1,  #  deprecated, do not use, also not use at pass culture except in one unit test
        "titre": 2,
        "titre_court": 3,
        "code_rayon_csr": 4,
        "disponibilite": 5,
        "collection": 6,
        "num_in_collection": 7,
        "categorie_de_prix": 8,  #  deprecated, do not use, also not use at pass culture
        "prix_ttc": 9,
        "editeur": 10,
        "distributeur": 11,
        "date_commercialisation": 12,
        "code_support": 13,
        "code_tva": 14,
        "nb_pages": 15,
        "longueur": 16,
        "largeur": 17,
        "epaisseur": 18,
        "poids": 19,
        "sujet": 20,  # not used at pass culture
        "statut_fiche": 21,
        "mise_en_vente": 22,  #  deprecated, do not use, also not used at pass culture
        "auteurs": 23,
        "date_creation": 24,
        "date_derniere_maj": 25,
        "taux_tva": 26,
        "libelle_code_rayon_csr": 27,
        "traducteur": 28,
        "langue_vo": 29,
        "critique_presse": 30,  #  deprecated, do not use, also not used at pass culture
        "commentaire": 31,
        "palmares_pro": 32,
        "image": 33,
        "code_edi_fournisseur": 34,
        "libelle_serie": 35,
        "id_genre_bd": 36,  #  deprecated, do not use, also not used at pass culture
        "libelle_genre_bd": 37,  #  deprecated, do not use, also not used at pass culture
        "numero_de_catalogue": 38,
        "scolaire": 39,
        "compteur_mp3": 40,
        "url_feuilleteur": 41,
        "id_auteur": 42,
        "indice_dewey": 43,
        "code_regroupement": 44,
    }
)
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
        self.product_whitelist_eans = {
            ean for ean, in fraud_models.ProductWhitelist.query.with_entities(fraud_models.ProductWhitelist.ean).all()
        }

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
            if book_unique_identifier in self.product_whitelist_eans:
                logger.info(
                    "Allowing ean=%s even if ineligible reason=%s as it is a whitelisted product",
                    book_unique_identifier,
                    ineligibility_reason,
                )
            else:
                logger.info("Ignoring ean=%s because reason=%s", book_unique_identifier, ineligibility_reason)
                try:
                    offers_api.delete_unwanted_existing_product(book_unique_identifier)
                except offers_exceptions.CannotDeleteProductWithBookings:
                    self.log_provider_event(
                        providers_models.LocalProviderEventType.SyncError,
                        f"Error deleting product with EAN: {self.product_infos['ean13']}",
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

        if self.product_infos["url_extrait_pdf"] != "":
            if product.mediaUrls is None:
                product.mediaUrls = []

            product.mediaUrls.append(self.product_infos["url_extrait_pdf"])

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
        encoding="iso-8859-1",
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
    infos["ean13"] = elts[COLUMN_INDICES["ean"]]
    infos["titre"] = elts[COLUMN_INDICES["titre"]]
    infos["titre_court"] = elts[COLUMN_INDICES["titre_court"]]
    infos["code_csr"] = elts[COLUMN_INDICES["code_rayon_csr"]]
    infos["code_dispo"] = elts[COLUMN_INDICES["disponibilite"]]
    infos["collection"] = elts[COLUMN_INDICES["collection"]]
    infos["num_in_collection"] = elts[COLUMN_INDICES["num_in_collection"]]
    infos["prix"] = elts[COLUMN_INDICES["prix_ttc"]]
    infos["editeur"] = elts[COLUMN_INDICES["editeur"]]
    infos["distributeur"] = elts[COLUMN_INDICES["distributeur"]]
    infos["date_parution"] = elts[COLUMN_INDICES["date_commercialisation"]]
    infos["code_support"] = elts[COLUMN_INDICES["code_support"]]
    infos["code_tva"] = elts[COLUMN_INDICES["code_tva"]]
    infos["n_pages"] = elts[COLUMN_INDICES["nb_pages"]]
    infos["longueur"] = elts[COLUMN_INDICES["longueur"]]
    infos["largeur"] = elts[COLUMN_INDICES["largeur"]]
    infos["epaisseur"] = elts[COLUMN_INDICES["epaisseur"]]
    infos["poids"] = elts[COLUMN_INDICES["poids"]]
    infos["is_update"] = elts[COLUMN_INDICES["statut_fiche"]]
    infos["auteurs"] = elts[COLUMN_INDICES["auteurs"]]
    infos["datetime_created"] = elts[COLUMN_INDICES["date_creation"]]
    infos["date_updated"] = elts[COLUMN_INDICES["date_derniere_maj"]]
    infos["taux_tva"] = elts[COLUMN_INDICES["taux_tva"]]
    infos["libelle_csr"] = elts[COLUMN_INDICES["libelle_code_rayon_csr"]]
    infos["traducteur"] = elts[COLUMN_INDICES["traducteur"]]
    infos["langue_orig"] = elts[COLUMN_INDICES["langue_vo"]]
    infos["commentaire"] = elts[COLUMN_INDICES["commentaire"]]
    infos["classement_top"] = elts[COLUMN_INDICES["palmares_pro"]]
    infos["has_image"] = elts[COLUMN_INDICES["image"]]
    infos["code_edi_fournisseur"] = elts[COLUMN_INDICES["code_edi_fournisseur"]]
    infos["libelle_serie_bd"] = elts[COLUMN_INDICES["libelle_genre_bd"]]
    infos["ref_editeur"] = elts[COLUMN_INDICES["numero_de_catalogue"]]
    infos["is_scolaire"] = elts[COLUMN_INDICES["scolaire"]]
    infos["n_extraits_mp3"] = elts[COLUMN_INDICES["compteur_mp3"]]
    infos["url_extrait_pdf"] = elts[COLUMN_INDICES["url_feuilleteur"]]
    infos["id_auteur"] = elts[COLUMN_INDICES["id_auteur"]]
    infos["indice_dewey"] = elts[COLUMN_INDICES["indice_dewey"]]
    infos["code_regroupement"] = elts[COLUMN_INDICES["code_regroupement"]]
    return infos


def get_extra_data_from_infos(infos: dict) -> offers_models.OfferExtraData:
    extra_data = offers_models.OfferExtraData()
    extra_data["author"] = infos["auteurs"]
    extra_data["ean"] = infos["ean13"]
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
