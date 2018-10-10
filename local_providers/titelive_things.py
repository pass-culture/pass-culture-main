import os
import re
from datetime import datetime
from pathlib import Path

from models.local_provider import LocalProvider, ProvidableInfo
from models.local_provider_event import LocalProviderEventType
from models.thing import Thing, BookFormat
from models import ThingType
from utils.string_processing import trim_with_elipsis

import ftplib
from io import TextIOWrapper, BytesIO

DATE_FORMAT = "%d/%m/%Y"
DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"
DATE_REGEXP = re.compile('Quotidien(\d+).tit')
FTP_TITELIVE = ftplib.FTP(os.environ.get("FTP_TITELIVE_URI"))


def read_date(date):
    return datetime.strptime(date, DATE_FORMAT)


def read_datetime(date):
    return datetime.strptime(date, DATETIME_FORMAT)


def file_date(filename):
    match = DATE_REGEXP.search(str(filename))
    if not match:
        raise ValueError('Invalid filename in titelive_works : '
                         + filename)
    return int(match.group(1))


def grp(pat, txt):
    r = re.search(pat, txt)
    return r.group(0) if r else '&'


class TiteLiveThings(LocalProvider):

    help = ""
    identifierDescription = "Pas d'identifiant nécessaire"\
                            + "(on synchronise tout)"
    identifierRegexp = None
    name = "TiteLive (Epagine / Place des libraires.com)"
    objectType = Thing
    canCreate = True

    def __init__(self, venueProvider, **options):
        super().__init__(venueProvider, **options)
        self.is_mock = False

        if 'mock' in options and options['mock']:
            self.is_mock = True
            data_root_path = Path(os.path.dirname(os.path.realpath(__file__)))\
                            / '..' / 'sandboxes' / 'providers' / 'titelive_works'
            data_thing_paths = data_root_path / 'livre3_11'
            all_thing_files = sorted(data_thing_paths.glob('Quotidien*.tit'))
            if not os.path.isdir(data_root_path):
                raise ValueError('File not found : '+str(data_root_path)
                                 + '\nDid you run "pc ftp_mirrors" ?')
        else:
            if "FTP_TITELIVE_USER" in os.environ:
                FTP_TITELIVE_USER = os.environ.get("FTP_TITELIVE_USER")
                FTP_TITELIVE_PWD = os.environ.get("FTP_TITELIVE_PWD")
                FTP_TITELIVE.login(FTP_TITELIVE_USER, FTP_TITELIVE_PWD)
                data_root_path = ''
                data_thing_paths = data_root_path + 'livre3_11/'

                # try:
                files_list = FTP_TITELIVE.nlst(data_thing_paths)
                # except ftplib.error_perm, resp:
                #     if str(resp) == "550 No files found":
                #         raise ValueError('File not found : '+str(data_root_path))
                #     else:
                #         raise ValueError('Error inconnue')
                files_list_final = [file_name for file_name in files_list if DATE_REGEXP.search(str(file_name))]

                all_thing_files = sorted(files_list_final)
            else:
                raise ValueError('Information de connexion non spécifiée.')

        if self.is_mock:
            ordered_thing_files = all_thing_files
        else:
            today = datetime.utcnow().day
            # Titelive 'Quotidien' files stay on the server only for about
            # 26 days. A file with today's date can therefore only be from
            # today, and should always be imported last
            ordered_thing_files = list(filter(lambda f: file_date(f) > today,
                                              all_thing_files))\
                                 + list(filter(lambda f: file_date(f) <= today,
                                               all_thing_files))

        latest_sync_part_end_event = self.latestSyncPartEndEvent()

        if latest_sync_part_end_event is None:
            self.thing_files = iter(ordered_thing_files)
        else:
            for index, filename in enumerate(ordered_thing_files):
                if file_date(filename) == int(latest_sync_part_end_event.payload):
                    self.thing_files = iter(ordered_thing_files[index+1:0])
                    break

        self.data_lines = None
        self.thing_file = None

    def open_next_file(self):
        if self.thing_file:
            self.logEvent(LocalProviderEventType.SyncPartEnd, file_date(self.thing_file))
        self.thing_file = self.thing_files.__next__()
        print("  Importing things from file "+str(self.thing_file))
        self.logEvent(LocalProviderEventType.SyncPartStart, file_date(self.thing_file))
        if self.is_mock:
            with open(self.thing_file, 'r', encoding='iso-8859-1') as f:
                self.data_lines = iter(f.readlines())
        else:
            data_file = BytesIO()
            data_wrapper = TextIOWrapper(
                data_file,
                encoding='iso-8859-1',
                # errors=None,         #  defalut
                # newline=None,        #  defalut
                line_buffering=True,
                # write_through=False  #  defalut
            )

            file_path = 'RETR '+ 'livre3_11/' + str(self.thing_file)
            FTP_TITELIVE.retrbinary(file_path, data_file.write)
            data_wrapper.seek(0, 0)
            self.data_lines = iter(data_wrapper.readlines())

    def __next__(self):
        if self.data_lines is None:
            self.open_next_file()
        try:
            elts = self.data_lines.__next__().split('~')
        except StopIteration:
            self.open_next_file()
            elts = self.data_lines.__next__().split('~')
        if len(elts) != 46:  # (45 elements from line + \n)
            print("Did not find 45 elements as expected in titelive"
                  + " line. Skipping line")
            return None
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
        infos['num_in_collection'] = elts[7]  # Variable/max 5	facultatif ( vide )	Numéro du titre au sein de la collection (pour le poche et les revues)
        infos['prix'] = elts[9]  # décimal / 2 chiffres après la virgule	Obligatoire	Prix public éditeur (TTC)
        infos['editeur'] = elts[10]  # Variable /max 40	Obligatoire	En capitales sans accent
        infos['distributeur'] = elts[11]  # Obligatoire	En capitales sans accent
        infos['date_parution'] = elts[12]  # jj/mm/aaaa	Obligatoire	01/01/2070 si inconnue
        infos['code_support'] = elts[13]  # Variable/max 2 caractères Obligatoire	voir table de correspondance SUPPORT (par exemple, poche). Le support TL correspond au format par défaut (c'est-à-dire sans indication précise de l'éditeur)
        infos['code_tva'] = elts[14]  # entier sur un chiffre	Obligatoire	voir table de correspondance TVA
        infos['n_pages'] = elts[15]  # entier	Facultatif ( par défaut 0 )
        infos['longueur'] = elts[16]  # décimal / 1 chiffre après la virgule	Facultatif ( par défaut 0 )	en centimètres
        infos['largeur'] = elts[17]  # décimal / 1 chiffre après la virgule	Facultatif ( par défaut 0 )	en centimètres
        infos['epaisseur'] = elts[18]  # décimal / 1 chiffre après la virgule	Facultatif ( par défaut 0 )	en centimètres
        infos['poids'] = elts[19]  # entier	Facultatif ( par défaut 0 )	en grammes
        infos['is_update'] = elts[21]  # entier de valeur 0 ou 1	0=Création,1=Modif	indique s'il s'agit d'un nouvelle fiche ou d'une fiche mise-à-jour mais déjà connue
        infos['auteurs'] = elts[23]  # Obligatoire	En minuscules accentuées
        infos['datetime_created'] = elts[24]  # jj/mm/aaaa hh:mm:ss	Obligatoire	création de la fiche (inutile pour exploitation de l'info sur un site marchand)
        infos['date_updated'] = elts[25]  # jj/mm/aaaa hh:mm:ss	Obligatoire	dernière mise à jour de la fiche (inutile pour exploitation de l'info sur un site marchand)
        infos['taux_tva'] = elts[26]  # décimal / deux chiffres après la virgule	Obligatoire
        infos['libelle_csr'] = elts[27]  # Variable  / max 80	Obligatoire	Libellé du rayon
        infos['traducteur'] = elts[28]  # Facultatif ( par défaut vide )	En minuscules accentuées
        infos['langue_orig'] = elts[29]  # Facultatif ( par défaut vide )
        infos['commentaire'] = elts[31]  # Facultatif	information qui complète le titre (sous-titre, edition collector, etc.)
        infos['classement_top'] = elts[32]  # Entier	Toujours si au Top 200	indication relative aux meilleures ventes de livre en France (1 signifie que le titre est classé n°1 au Top 200 de la semaine).
        infos['has_image'] = elts[33]  # entier de valeur 0 ou 1	Obligatoire	1 si référence avec image
        infos['code_edi_fournisseur'] = elts[34]  # 13 caractères	Obligatoire	numéro utile pour les commande EDI
        infos['libelle_serie_bd'] = elts[35]  # Facultatif
        infos['ref_editeur'] = elts[38]  # 12 caractères	Facultatif	référence interne aux éditeurs, utilisé en scolaire
        infos['is_scolaire'] = elts[39]  # entier de valeur 0 ou 1	Toujours	permet d'identifier les ouvrages scolaires ; 0 : non ; 1 : oui
        infos['n_extraits_mp3'] = elts[40]  # Entier	Toujours	nombre d'extraits sonores associés à la réf
        infos['url_extrait_pdf'] = elts[41]  # Facultatif ( par défaut vide )	extrait pdf de l'oeuvre
        infos['id_auteur'] = elts[42]  # Entier	Facultatif ( par défaut vide )	permet de faire le lien entre l'auteur et sa biographie
        infos['indice_dewey'] = elts[43]  # Facultatif ( par défaut vide )
        infos['code_regroupement'] = elts[44]  # Entier	Obligatoire	permet de faire le lien entre les mêmes œuvres ; 0 si non regroupé

        self.infos = infos
        self.extraData = {}

        tl_type = infos['code_support']
        if tl_type == 'A':   # AUTRE SUPPORT
            return None
        elif tl_type == 'BD':  # BANDE DESSINEE
            self.thing_type = ThingType.LIVRE_EDITION.name
        elif tl_type == 'BL':  # BEAUX LIVRES
            self.thing_type = ThingType.LIVRE_EDITION.name
            self.extraData['bookFormat'] = BookFormat.Hardcover.value
        elif tl_type == 'C':   # CARTE & PLAN
            #self.thing_type = ThingType.Map
            return None
        elif tl_type == 'CA':  # CD AUDIO
            #self.thing_type = ThingType.MusicRecording
            return None
        elif tl_type == 'CB':  # COFFRET / BOITE
            return None
        elif tl_type == 'CD':  # CD-ROM
            return None
        elif tl_type == 'CL':  # CALENDRIER
            return None
        elif tl_type == 'DV':  # DVD
            #self.thing_type = ThingType.Movie
            return None
        elif tl_type == 'EB':  # CONTENU NUMERIQUE
            return
        elif tl_type == 'K7':  # CASSETTE AUDIO VIDEO
            return None
        elif tl_type == 'LA':  # LIVRE ANCIEN
            self.thing_type = ThingType.LIVRE_EDITION.name
        elif tl_type == 'LC':  # LIVRE + CASSETTE
            return None
        elif tl_type == 'LD':  # LIVRE + CD AUDIO
            return None
        elif tl_type == 'LE':  # LIVRE NUMERIQUE
            self.thing_type = ThingType.LIVRE_EDITION.name
            self.extraData['bookFormat'] = BookFormat.EBook.value
        elif tl_type == 'LR':  # LIVRE + CD-ROM
            return None
        elif tl_type == 'LT':  # LISEUSES & TABLETTES
            return None
        elif tl_type == 'LV':  # LIVRE+DVD
            return None
        elif tl_type == 'M':   # MOYEN FORMAT
            return None
        elif tl_type == 'O':   # OBJET
            return None
        elif tl_type == 'P':   # POCHE
            self.thing_type = ThingType.LIVRE_EDITION.name
            self.extraData['bookFormat'] = BookFormat.Paperback.value
        elif tl_type == 'PC':  # PAPETERIE COLORIAGE
            return None
        elif tl_type == 'PS':  # POSTER
            return None
        elif tl_type == 'R':   # REVUE
            return None
        elif tl_type == 'T'\
             or tl_type == 'TL':   # TL  Le support TL correspond au format par défaut (c'est-à-dire sans indication précise de l'éditeur)
            self.thing_type = ThingType.LIVRE_EDITION.name  # (hopefully)
        elif tl_type == 'TR':  # TRANSPARENTS
            return None
        else:
            print(" WARNING: Unknown tl_type: "+tl_type)
            return None

        p_info = ProvidableInfo()
        p_info.type = Thing
        p_info.idAtProviders = infos['ean13']
        p_info.dateModifiedAtProvider = read_date(infos['date_updated'])
        return p_info

    def updateObject(self, thing):
        infos = self.infos

        assert thing.idAtProviders == infos['ean13']

        thing.extraData = self.extraData
        thing.name = trim_with_elipsis(infos['titre'], 140)
        thing.datePublished = read_date(infos['date_parution'])
        thing.extraData['author'] = infos['auteurs']
        thing.type = self.thing_type

        if infos['indice_dewey'] != '':
            thing.extraData['dewey'] = infos['indice_dewey']
        thing.extraData['titelive_regroup'] = infos['code_regroupement']
        thing.extraData['prix_livre'] = infos['prix'].replace(',', '.')
        thing.extraData['rayon'] = infos['libelle_csr']
        if infos['is_scolaire'] == '1':
            thing.extraData['schoolbook'] = True
        if infos['classement_top'] != '':
            thing.extraData['top'] = infos['classement_top']
        if infos['collection'] != '':
            thing.extraData['collection'] = infos['collection']
        if infos['num_in_collection'] != '':
            thing.extraData['num_in_collection'] = infos['num_in_collection']
        if infos['libelle_serie_bd'] != '':
            thing.extraData['comic_series'] = infos['libelle_serie_bd']
        if infos['commentaire'] != '':
            thing.extraData['comment'] = trim_with_elipsis(infos['commentaire'], 92)

        if infos['url_extrait_pdf'] != '':
            thing.mediaUrls.append(infos['url_extrait_pdf'])
