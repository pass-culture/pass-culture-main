import re
from io import TextIOWrapper, BytesIO
from typing import Dict

from connectors.ftp_titelive import get_files_to_process_from_titelive_ftp, connect_to_titelive_ftp
from domain.titelive import get_date_from_filename, read_things_date
from local_providers.local_provider import LocalProvider
from local_providers.providable_info import ProvidableInfo
from models import Product, ThingType, BookFormat
from models.local_provider_event import LocalProviderEventType
from repository import local_provider_event_queries
from utils.logger import logger
from utils.string_processing import trim_with_elipsis

DATE_REGEXP = re.compile('([a-zA-Z]+)(\d+).tit')
THINGS_FOLDER_NAME_TITELIVE = 'livre3_11'
NUMBER_OF_ELEMENTS_PER_LINE = 46  # (45 elements from line + \n)


class TiteLiveThings(LocalProvider):
    help = ""
    identifierDescription = "Pas d'identifiant nécessaire" \
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "TiteLive (Epagine / Place des libraires.com)"
    object_type = Product
    canCreate = True

    def __init__(self):
        super().__init__()

        ordered_thing_files = get_files_to_process_from_titelive_ftp(THINGS_FOLDER_NAME_TITELIVE, DATE_REGEXP)
        self.thing_files = self.get_remaining_files_to_check(ordered_thing_files)

        self.data_lines = None
        self.thing_file = None

    def open_next_file(self):
        if self.thing_file:
            self.log_provider_event(LocalProviderEventType.SyncPartEnd,
                                    get_date_from_filename(self.thing_file, DATE_REGEXP))
        self.thing_file = next(self.thing_files)
        logger.info("  Importing things from file %s" % self.thing_file)
        self.log_provider_event(LocalProviderEventType.SyncPartStart,
                                get_date_from_filename(self.thing_file, DATE_REGEXP))

        self.data_lines = get_lines_from_thing_file(str(self.thing_file))

    def __next__(self):
        if self.data_lines is None:
            self.open_next_file()

        try:
            data_lines = next(self.data_lines)
            elements = data_lines.split('~')
        except StopIteration:
            self.open_next_file()
            elements = next(self.data_lines).split('~')

        if len(elements) != NUMBER_OF_ELEMENTS_PER_LINE:
            logger.debug("Did not find 45 elements as expected in titelive"
                         + " line. Skipping line")
            return None

        self.infos = get_infos_from_data_line(elements)

        if self.infos['is_scolaire'] == '1':
            return None

        self.extraData = {}

        self.thing_type, self.extraData['bookFormat'] = get_thing_type_and_extra_data_from_titelive_type(
            self.infos['code_support'])

        if self.thing_type is None:
            return None

        providable_info = ProvidableInfo()
        providable_info.type = Product
        providable_info.id_at_providers = self.infos['ean13']
        providable_info.date_modified_at_provider = read_things_date(self.infos['date_updated'])
        return [providable_info]

    def updateObject(self, thing):
        assert thing.idAtProviders == self.infos['ean13']

        thing.name = trim_with_elipsis(self.infos['titre'], 140)
        thing.datePublished = read_things_date(self.infos['date_parution'])
        thing.type = self.thing_type
        thing.extraData = self.extraData.copy()
        thing.extraData.update(get_extra_data_from_infos(self.infos))

        if self.infos['url_extrait_pdf'] != '':
            if thing.mediaUrls is None:
                thing.mediaUrls = []

            thing.mediaUrls.append(self.infos['url_extrait_pdf'])

    def get_remaining_files_to_check(self, ordered_thing_files: list):
        latest_sync_part_end_event = local_provider_event_queries.find_latest_sync_part_end_event(self.provider)
        if latest_sync_part_end_event is None:
            return iter(ordered_thing_files)
        else:
            for index, filename in enumerate(ordered_thing_files):
                if get_date_from_filename(filename, DATE_REGEXP) == int(latest_sync_part_end_event.payload):
                    return iter(ordered_thing_files[index + 1:])


def get_lines_from_thing_file(thing_file: str):
    data_file = BytesIO()
    data_wrapper = TextIOWrapper(
        data_file,
        encoding='iso-8859-1',
        line_buffering=True,
    )
    file_path = 'RETR ' + THINGS_FOLDER_NAME_TITELIVE + '/' + thing_file
    connect_to_titelive_ftp().retrbinary(file_path, data_file.write)
    data_wrapper.seek(0, 0)
    return iter(data_wrapper.readlines())


def get_thing_type_and_extra_data_from_titelive_type(titelive_type):
    if titelive_type == 'A':
        return None, None
    elif titelive_type == 'BD':
        return str(ThingType.LIVRE_EDITION), BookFormat.BANDE_DESSINEE.value
    elif titelive_type == 'BL':
        return str(ThingType.LIVRE_EDITION), BookFormat.BEAUX_LIVRES.value
    elif titelive_type == 'C':
        return None, None
    elif titelive_type == 'CA':
        return None, None
    elif titelive_type == 'CB':
        return None, None
    elif titelive_type == 'CD':
        return None, None
    elif titelive_type == 'CL':
        return None, None
    elif titelive_type == 'DV':
        return None, None
    elif titelive_type == 'EB':
        return None, None
    elif titelive_type == 'K7':
        return None, None
    elif titelive_type == 'LA':
        return None, None
    elif titelive_type == 'LC':
        return str(ThingType.LIVRE_EDITION), BookFormat.LIVRE_CASSETTE.value
    elif titelive_type == 'LD':
        return str(ThingType.LIVRE_EDITION), BookFormat.LIVRE_AUDIO.value
    elif titelive_type == 'LE':
        return None, None
    elif titelive_type == 'LR':
        return None, None
    elif titelive_type == 'LT':
        return None, None
    elif titelive_type == 'LV':
        return None, None
    elif titelive_type == 'M':
        return str(ThingType.LIVRE_EDITION), BookFormat.MOYEN_FORMAT.value
    elif titelive_type == 'O':
        return None, None
    elif titelive_type == 'P':
        return str(ThingType.LIVRE_EDITION), BookFormat.POCHE.value
    elif titelive_type == 'PC':
        return None, None
    elif titelive_type == 'PS':
        return None, None
    elif titelive_type == 'R':
        return str(ThingType.LIVRE_EDITION), BookFormat.REVUE.value
    elif titelive_type == 'T' \
            or titelive_type == 'TL':
        return str(ThingType.LIVRE_EDITION), None
    elif titelive_type == 'TR':
        return None, None
    else:
        logger.debug(" WARNING: Unknown titelive_type: " + titelive_type)
        return None, None


def get_infos_from_data_line(elts: []):
    infos = {}
    infos['ean13'] = elts[0]
    infos['isbn'] = elts[1]
    infos['titre'] = elts[2]
    infos['titre_court'] = elts[3]
    infos['code_csr'] = elts[4]
    infos['code_dispo'] = elts[5]
    infos['collection'] = elts[6]
    infos['num_in_collection'] = elts[7]
    infos['prix'] = elts[9]
    infos['editeur'] = elts[10]
    infos['distributeur'] = elts[11]
    infos['date_parution'] = elts[12]
    infos['code_support'] = elts[13]
    infos['code_tva'] = elts[14]
    infos['n_pages'] = elts[15]
    infos['longueur'] = elts[16]
    infos['largeur'] = elts[17]
    infos['epaisseur'] = elts[18]
    infos['poids'] = elts[19]
    infos['is_update'] = elts[21]
    infos['auteurs'] = elts[23]
    infos['datetime_created'] = elts[24]
    infos['date_updated'] = elts[25]
    infos['taux_tva'] = elts[26]
    infos['libelle_csr'] = elts[27]
    infos['traducteur'] = elts[28]
    infos['langue_orig'] = elts[29]
    infos['commentaire'] = elts[31]
    infos['classement_top'] = elts[32]
    infos['has_image'] = elts[33]
    infos['code_edi_fournisseur'] = elts[34]
    infos['libelle_serie_bd'] = elts[35]
    infos['ref_editeur'] = elts[38]
    infos['is_scolaire'] = elts[39]
    infos['n_extraits_mp3'] = elts[40]
    infos['url_extrait_pdf'] = elts[41]
    infos['id_auteur'] = elts[42]
    infos['indice_dewey'] = elts[43]
    infos['code_regroupement'] = elts[44]
    return infos


def get_extra_data_from_infos(infos: Dict) -> Dict:
    extra_data = dict()
    extra_data['author'] = infos['auteurs']
    extra_data['isbn'] = infos['isbn']
    if infos['indice_dewey'] != '':
        extra_data['dewey'] = infos['indice_dewey']
    extra_data['titelive_regroup'] = infos['code_regroupement']
    extra_data['prix_livre'] = infos['prix'].replace(',', '.')
    extra_data['rayon'] = infos['libelle_csr']
    if infos['is_scolaire'] == '1':
        extra_data['schoolbook'] = True
    if infos['classement_top'] != '':
        extra_data['top'] = infos['classement_top']
    if infos['collection'] != '':
        extra_data['collection'] = infos['collection']
    if infos['num_in_collection'] != '':
        extra_data['num_in_collection'] = infos['num_in_collection']
    if infos['libelle_serie_bd'] != '':
        extra_data['comic_series'] = infos['libelle_serie_bd']
    if infos['commentaire'] != '':
        extra_data['comment'] = trim_with_elipsis(infos['commentaire'], 92)
    return extra_data
