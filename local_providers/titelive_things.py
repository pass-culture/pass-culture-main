import os
import re
from pathlib import Path

from models.local_provider import LocalProvider, ProvidableInfo
from models.local_provider_event import LocalProviderEventType
from models.thing import Thing, BookFormat
from models import ThingType
from repository import local_provider_event_queries
from utils.ftp_titelive import get_titelive_ftp, get_ordered_thing_files_from_titelive_ftp, \
    get_date_from_thing_filename, read_date
from utils.logger import logger
from utils.string_processing import trim_with_elipsis

from io import TextIOWrapper, BytesIO

DATE_REGEXP = re.compile('(\w+)(\d+).tit')
THINGS_FOLDER_NAME_TITELIVE = 'livre3_11'
INIT_FULL_TABLE = 'FullTable*.tit'


class TiteLiveThings(LocalProvider):
    help = ""
    identifierDescription = "Pas d'identifiant nécessaire" \
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "TiteLive (Epagine / Place des libraires.com)"
    objectType = Thing
    canCreate = True

    def __init__(self, venueProvider, **options):
        super().__init__(venueProvider, **options)
        self.is_mock = 'mock' in options and options['mock']
        self.file_to_import = 'file_to_import' in options and options['file_to_import']

        logger.info("In __init__")
        if self.file_to_import:
            ordered_thing_files = get_ordered_thing_files_from_init_file(self.file_to_import)
        else:
            ordered_thing_files = get_ordered_thing_files_from_titelive_ftp(THINGS_FOLDER_NAME_TITELIVE, DATE_REGEXP)

        self.thing_files = self.get_remaining_files_to_check(ordered_thing_files)
        self.data_lines = None
        self.thing_file = None

    def open_next_file(self):
        logger.info("In open_next")
        if self.thing_file:
            self.logProviderEvent(LocalProviderEventType.SyncPartEnd,
                                  get_date_from_thing_filename(self.thing_file, DATE_REGEXP))
        self.thing_file = self.thing_files.__next__()
        logger.info("  Importing things from file %s" % self.thing_file)
        self.logProviderEvent(LocalProviderEventType.SyncPartStart,
                              get_date_from_thing_filename(self.thing_file, DATE_REGEXP))

        self.data_lines = get_lines_from_thing_file(str(self.thing_file))

    def __next__(self):
        if self.data_lines is None:
            self.open_next_file()

        try:
            data_lines = self.data_lines.__next__()
            elements = data_lines.split('~')
        except StopIteration:
            self.open_next_file()
            elements = self.data_lines.__next__().split('~')

        if len(elements) != 46:  # (45 elements from line + \n)
            logger.info("Did not find 45 elements as expected in titelive"
                        + " line. Skipping line")
            return None

        self.infos = self.get_infos_from_data_line(elements)
        self.extraData = {}

        self.thing_type, self.extraData['bookFormat'] = get_thing_type_and_extra_data_from_titelive_type(
            self.infos['code_support'])

        if self.thing_type is None:
            return None

        providable_info = ProvidableInfo()
        providable_info.type = Thing
        providable_info.idAtProviders = self.infos['ean13']
        providable_info.dateModifiedAtProvider = read_date(self.infos['date_updated'])
        return providable_info

    def updateObject(self, thing):
        assert thing.idAtProviders == self.infos['ean13']

        thing.name = trim_with_elipsis(self.infos['titre'], 140)
        thing.datePublished = read_date(self.infos['date_parution'])
        thing.type = self.thing_type
        thing.extraData = self.get_extraData_from_infos()

        if self.infos['url_extrait_pdf'] != '':
            thing.mediaUrls.append(self.infos['url_extrait_pdf'])

    def get_extraData_from_infos(self):
        extraData = self.extraData
        extraData['author'] = self.infos['auteurs']
        if self.infos['indice_dewey'] != '':
            extraData['dewey'] = self.infos['indice_dewey']
        extraData['titelive_regroup'] = self.infos['code_regroupement']
        extraData['prix_livre'] = self.infos['prix'].replace(',', '.')
        extraData['rayon'] = self.infos['libelle_csr']
        if self.infos['is_scolaire'] == '1':
            extraData['schoolbook'] = True
        if self.infos['classement_top'] != '':
            extraData['top'] = self.infos['classement_top']
        if self.infos['collection'] != '':
            extraData['collection'] = self.infos['collection']
        if self.infos['num_in_collection'] != '':
            extraData['num_in_collection'] = self.infos['num_in_collection']
        if self.infos['libelle_serie_bd'] != '':
            extraData['comic_series'] = self.infos['libelle_serie_bd']
        if self.infos['commentaire'] != '':
            extraData['comment'] = trim_with_elipsis(self.infos['commentaire'], 92)

        return extraData

    def get_infos_from_data_line(self, elts: []):
        infos = {}
        infos['ean13'] = elts[0]
        infos['isbn'] = elts[1]  # Facultatif
        infos['titre'] = elts[2]  # long max 250, Obligatoire, En minuscules accentuées
        infos['titre_court'] = elts[3]  # Variable/max 250	Obligatoire	inutile pour exploitation sur un site marchand
        infos['code_csr'] = elts[4]  # Obligatoire	Il s'agit des codes RAYON (voir table de correspondance)
        infos['code_dispo'] = elts[5]  # Obligatoire
        # 2 = Pas encore paru donc à paraître
        # 3 = Réimpression en cours en revanche nous ne disposons pas d’info sur la date de réimpression
        # 4 = Non disponible provisoirement il peut s’agir d’une rupture de stock très brève chez le distributeur
        # et la référence doit donc en principe être à nouveau disponible dans un délai assez court
        # 5 = Ne sera plus distribué par nous un distributeur annonce ainsi que cette référence va être bientôt distribué par une autre société. Dès que l’on a l’information l’ouvrage passe en disponible avec le nom du nouveau distributeur)
        # 6 = Arrêt définitif de commercialisation
        # 7 = Manque sans date code très peu utilisé
        # et équivalent au code 4
        # 8 = A reparaître donc réédition en cours (NB : en principe la référence est alors rééditée sous un nouveau gencode)
        # 9 = Abandon de parution
        infos['collection'] = elts[6]  # Variable/max 160	Oui si collection	En minuscules accentuées
        infos['num_in_collection'] = elts[
            7]  # Variable/max 5	facultatif ( vide )	Numéro du titre au sein de la collection (pour le poche et les revues)
        infos['prix'] = elts[9]  # décimal / 2 chiffres après la virgule	Obligatoire	Prix public éditeur (TTC)
        infos['editeur'] = elts[10]  # Variable /max 40	Obligatoire	En capitales sans accent
        infos['distributeur'] = elts[11]  # Obligatoire	En capitales sans accent
        infos['date_parution'] = elts[12]  # jj/mm/aaaa	Obligatoire	01/01/2070 si inconnue
        infos['code_support'] = elts[
            13]  # Variable/max 2 caractères Obligatoire	voir table de correspondance SUPPORT (par exemple, poche). Le support TL correspond au format par défaut (c'est-à-dire sans indication précise de l'éditeur)
        infos['code_tva'] = elts[14]  # entier sur un chiffre	Obligatoire	voir table de correspondance TVA
        infos['n_pages'] = elts[15]  # entier	Facultatif ( par défaut 0 )
        infos['longueur'] = elts[16]  # décimal / 1 chiffre après la virgule	Facultatif ( par défaut 0 )	en centimètres
        infos['largeur'] = elts[17]  # décimal / 1 chiffre après la virgule	Facultatif ( par défaut 0 )	en centimètres
        infos['epaisseur'] = elts[18]  # décimal / 1 chiffre après la virgule	Facultatif ( par défaut 0 )	en centimètres
        infos['poids'] = elts[19]  # entier	Facultatif ( par défaut 0 )	en grammes
        infos['is_update'] = elts[
            21]  # entier de valeur 0 ou 1	0=Création,1=Modif	indique s'il s'agit d'un nouvelle fiche ou d'une fiche mise-à-jour mais déjà connue
        infos['auteurs'] = elts[23]  # Obligatoire	En minuscules accentuées
        infos['datetime_created'] = elts[
            24]  # jj/mm/aaaa hh:mm:ss	Obligatoire	création de la fiche (inutile pour exploitation de l'info sur un site marchand)
        infos['date_updated'] = elts[
            25]  # jj/mm/aaaa hh:mm:ss	Obligatoire	dernière mise à jour de la fiche (inutile pour exploitation de l'info sur un site marchand)
        infos['taux_tva'] = elts[26]  # décimal / deux chiffres après la virgule	Obligatoire
        infos['libelle_csr'] = elts[27]  # Variable  / max 80	Obligatoire	Libellé du rayon
        infos['traducteur'] = elts[28]  # Facultatif ( par défaut vide )	En minuscules accentuées
        infos['langue_orig'] = elts[29]  # Facultatif ( par défaut vide )
        infos['commentaire'] = elts[
            31]  # Facultatif	information qui complète le titre (sous-titre, edition collector, etc.)
        infos['classement_top'] = elts[
            32]  # Entier	Toujours si au Top 200	indication relative aux meilleures ventes de livre en France (1 signifie que le titre est classé n°1 au Top 200 de la semaine).
        infos['has_image'] = elts[33]  # entier de valeur 0 ou 1	Obligatoire	1 si référence avec image
        infos['code_edi_fournisseur'] = elts[34]  # 13 caractères	Obligatoire	numéro utile pour les commande EDI
        infos['libelle_serie_bd'] = elts[35]  # Facultatif
        infos['ref_editeur'] = elts[38]  # 12 caractères	Facultatif	référence interne aux éditeurs, utilisé en scolaire
        infos['is_scolaire'] = elts[
            39]  # entier de valeur 0 ou 1	Toujours	permet d'identifier les ouvrages scolaires ; 0 : non ; 1 : oui
        infos['n_extraits_mp3'] = elts[40]  # Entier	Toujours	nombre d'extraits sonores associés à la réf
        infos['url_extrait_pdf'] = elts[41]  # Facultatif ( par défaut vide )	extrait pdf de l'oeuvre
        infos['id_auteur'] = elts[
            42]  # Entier	Facultatif ( par défaut vide )	permet de faire le lien entre l'auteur et sa biographie
        infos['indice_dewey'] = elts[43]  # Facultatif ( par défaut vide )
        infos['code_regroupement'] = elts[
            44]  # Entier	Obligatoire	permet de faire le lien entre les mêmes œuvres ; 0 si non regroupé
        return infos

    def get_remaining_files_to_check(self, ordered_thing_files):
        latest_sync_part_end_event = local_provider_event_queries.find_latest_sync_part_end_event(self.dbObject)
        if latest_sync_part_end_event is None:
            return iter(ordered_thing_files)
        else:
            for index, filename in enumerate(ordered_thing_files):
                if get_date_from_thing_filename(filename, DATE_REGEXP) == int(latest_sync_part_end_event.payload):
                    return iter(ordered_thing_files[index + 1:0])


def get_lines_from_thing_file(thing_file: str):
    data_file = BytesIO()
    data_wrapper = TextIOWrapper(
        data_file,
        encoding='iso-8859-1',
        line_buffering=True,
    )
    file_path = 'RETR ' + THINGS_FOLDER_NAME_TITELIVE + '/' + thing_file
    get_titelive_ftp().retrbinary(file_path, data_file.write)
    data_wrapper.seek(0, 0)
    return iter(data_wrapper.readlines())


def get_ordered_thing_files_from_init_file(file_to_import):
    data_root_path = Path(os.path.dirname(os.path.realpath(__file__))) \
                     / '..' / 'sandboxes' / 'providers' / 'titelive_works'
    data_thing_paths = data_root_path
    all_thing_files = sorted(data_thing_paths.glob(file_to_import))
    return all_thing_files


def get_thing_type_and_extra_data_from_titelive_type(titelive_type):
    if titelive_type == 'A':  # AUTRE SUPPORT
        return None, None
    elif titelive_type == 'BD':  # BANDE DESSINEE
        return str(ThingType.LIVRE_EDITION), None
    elif titelive_type == 'BL':  # BEAUX LIVRES
        return str(ThingType.LIVRE_EDITION), BookFormat.Hardcover.value
    elif titelive_type == 'C':  # CARTE & PLAN
        # self.thing_type = ThingType.Map
        return None, None
    elif titelive_type == 'CA':  # CD AUDIO
        # return ThingType.MusicRecording
        return None, None
    elif titelive_type == 'CB':  # COFFRET / BOITE
        return None, None
    elif titelive_type == 'CD':  # CD-ROM
        return None, None
    elif titelive_type == 'CL':  # CALENDRIER
        return None, None
    elif titelive_type == 'DV':  # DVD
        # return ThingType.Movie
        return None, None
    elif titelive_type == 'EB':  # CONTENU NUMERIQUE
        return None, None
    elif titelive_type == 'K7':  # CASSETTE AUDIO VIDEO
        return None, None
    elif titelive_type == 'LA':  # LIVRE ANCIEN
        return str(ThingType.LIVRE_EDITION), None
    elif titelive_type == 'LC':  # LIVRE + CASSETTE
        return None, None
    elif titelive_type == 'LD':  # LIVRE + CD AUDIO
        return None, None
    elif titelive_type == 'LE':  # LIVRE NUMERIQUE
        return str(ThingType.LIVRE_EDITION), BookFormat.EBook.value
    elif titelive_type == 'LR':  # LIVRE + CD-ROM
        return None, None
    elif titelive_type == 'LT':  # LISEUSES & TABLETTES
        return None, None
    elif titelive_type == 'LV':  # LIVRE+DVD
        return None, None
    elif titelive_type == 'M':  # MOYEN FORMAT
        return None, None
    elif titelive_type == 'O':  # OBJET
        return None, None
    elif titelive_type == 'P':  # POCHE
        return str(ThingType.LIVRE_EDITION), BookFormat.Paperback.value
    elif titelive_type == 'PC':  # PAPETERIE COLORIAGE
        return None, None
    elif titelive_type == 'PS':  # POSTER
        return None, None
    elif titelive_type == 'R':  # REVUE
        return None, None
    elif titelive_type == 'T' \
            or titelive_type == 'TL':  # TL  Le support TL correspond au format par défaut (c'est-à-dire sans indication précise de l'éditeur)
        return str(ThingType.LIVRE_EDITION), None  # (hopefully)
    elif titelive_type == 'TR':  # TRANSPARENTS
        return None, None
    else:
        logger.info(" WARNING: Unknown titelive_type: " + titelive_type)
        return None, None
