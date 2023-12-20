import csv
from datetime import datetime
import enum
import json
import os
import pathlib

from fuzzywuzzy import fuzz

from pcapi.core.offerers.models import Venue
from pcapi.utils import requests


ACCESLIBRE_API_KEY = ""  # API key to request to Acceslibre
API_URL = "https://acceslibre.beta.gouv.fr/api"
PATH = pathlib.Path(__file__).parent.resolve()
REQUEST_PAGE_SIZE = 100
NAME_TOLERANCE = 20


class AccesLibreException(Exception):
    pass


class ERP_Activity(enum.Enum):
    """
    Enum des slugs d'activité de AccesLibre
    """

    ADMINISTRATION_PUBLIQUE = "administration-publique"
    AQUARIUM = "aquarium"
    ART = "art"
    BIBLIOTHEQUE = "bibliotheque-mediatheque"
    CHATEAU = "chateau"
    CENTRE_CULTUREL = "centre-culturel"
    CINEMA = "cinema"
    ARTISANAT = "artisanat"
    ECOLE_DE_MUSIQUE = "conservatoire-et-ecole-de-musique"
    COLLECTIVITE_TERRITORIALE = "collectivite-territoriale"
    DISQUAIRE = "disquaire"
    ECOLE_DE_DANSE = "ecole-de-danse"
    ENCADREUR = "encadreur-enlumineur"
    EVENEMENT_CULTUREL = "evenement-culturel"
    GALERIE_D_ART = "salle-dexposition"
    GYMNASE = "gymnase"
    INSTRUMENT_DE_MUSIQUE = "instruments-et-materiel-de-musique"
    LIBRAIRIE = "librairie"
    LIEU_DE_VISITE = "lieu-de-visite"
    LOISIRS_CREATIFS = "loisirs-creatifs"
    MENUISERIE = "menuiserie-ebenisterie"
    MONUMENT_HISTORIQUE = "monument-historique"
    MUSEE = "musee"
    MUSIQUE = "musique"
    OPERA = "opera"
    PAPETERIE = "papeterie-presse-journaux"
    PARC_DES_EXPOSITIONS = "parc-des-expositions"
    SALLE_DE_CONCERT = "salle-de-concert"
    SALLE_DE_DANSE = "salle-de-danse"
    SALLE_DES_FETES = "salle-des-fetes"
    SALLE_DE_SPECTACLE = "salle-de-spectacle"
    THEATRE = "theatre"


def save_permanent_venues_in_json(
    pc_venue_file: pathlib.Path,
) -> None:
    """
    Save our venues data into a json file (in order to avoid too many db requests)
    It can also be done directly from metabase, but at the time of writing this script
    data were unavailable
    """
    permanent_venues = Venue.query.filter(Venue.isPermanent == True, Venue.isVirtual == False).all()
    venue_output = []
    for venue in permanent_venues:
        venue_output.append(
            {
                "Venue ID": venue.id,
                "Venue Ban Id": venue.banId,
                "Venue Name": venue.name,
                "Venue Postal Code": venue.postalCode,
                "Venue City": venue.city,
                "Venue Address": venue.address,
                "Venue Activity": venue.venueTypeCode.value,
            }
        )
    with open(pc_venue_file, "w", encoding="utf-8") as output_file:
        json.dump(venue_output, output_file, indent=2)


def request_acceslibre_api_and_save_output(
    acceslibre_file: pathlib.Path,
) -> None:
    """
    Request erps infos by activity, with batch size limited requests
    and save them in several a json files named by activities
    """
    for activity in ERP_Activity:
        erp_list = []
        print(f"requesting all {activity.value}")
        headers = {"Content-Type": "application/json", "Authorization": f"Api-Key {ACCESLIBRE_API_KEY}"}

        # First request to get number of pages
        url = f"{API_URL}/erps/?page_size={REQUEST_PAGE_SIZE}&page={1}&activite={activity.value}"
        response = requests.get(url, headers=headers)
        try:
            results_count = response.json()["count"]
        except requests.exceptions.Timeout:
            raise AccesLibreException(f"Error connecting AccessLibre API for erps {activity}")

        page_number = int(results_count / REQUEST_PAGE_SIZE) + 1

        # Request by page
        for page in range(1, page_number + 1):
            url = f"{API_URL}/erps/?page_size={REQUEST_PAGE_SIZE}&page={page}&activite={activity.value}"
            try:
                response = requests.get(url, headers=headers)
            except requests.exceptions.Timeout:
                raise AccesLibreException(f"Error connecting AccessLibre API for erps {activity}")
            print(f"requesting page {page} / {page_number} OK")
            erp_list.extend(response.json()["results"])
        acceslibre_activity_file = PATH / f"data/acceslibre_{activity.name}.json"
        with open(acceslibre_activity_file, "w", encoding="utf-8") as output_file:
            json.dump(erp_list, output_file)


def merge_acceslibre_json_files() -> None:
    """
    Once all erps from acceslibre have been requested and saved by
    activity in json files, we merge those json files together
    """
    files = []
    for activity in ERP_Activity:
        acceslibre_file = str(PATH) + f"/data/acceslibre_{activity.name}.json"
        if os.path.exists(acceslibre_file):
            files.append(acceslibre_file)
    result = []
    for file in files:
        with open(file, "r", encoding="utf-8") as content:
            result.extend(json.load(content))

    with open(PATH / "data/acceslibre_all.json", "w", encoding="utf-8") as output_file:
        json.dump(result, output_file)


def remove_duplication(acceslibre_file: pathlib.Path) -> None:
    """
    Removes duplicates from the JSON file received by our request
    to acceslibre API
    """
    with open(acceslibre_file, "r", encoding="utf-8") as json_file:
        data = json.load(json_file)

    unique_data = set()
    data_clean = []
    for entry in data:
        if json.dumps(entry, sort_keys=True) not in unique_data:
            data_clean.append(entry)
            unique_data.add(json.dumps(entry, sort_keys=True))

    with open(acceslibre_file, "w", encoding="utf-8") as fichier_sortie:
        json.dump(data_clean, fichier_sortie, indent=2)


def find_match(
    pc_venue_file: pathlib.Path,
    acceslibre_file: pathlib.Path,
) -> list[dict]:
    """
    Matching data between the two JSON files pc_venue_file and
    acceslibre_file. First we match BAN IDs, then we match names

    Here we kept differents acceptabilities thresholds to
    find the appropriate one for future match
    """
    venue_ids = set()
    # match_list = []
    with open(pc_venue_file, "r", encoding="utf-8") as file:
        venue_list = json.load(file)

    with open(acceslibre_file, "r", encoding="utf-8") as read_file:
        erp_list = json.load(read_file)

    mapping = {v["Venue Ban Id"]: v for v in venue_list}

    # trying several matchings
    match_list_contains = [{"name_match": "Un nom est contenu dans l'autre", "Ban ID": ""}]
    match_list_50_100 = [{"name_match": "Entre 50 et 100%", "Ban ID": ""}]
    match_list_35_50 = [{"name_match": "Entre 35 et 50%", "Ban ID": ""}]
    match_list_20_35 = [{"name_match": "Entre 20% et 35 %", "Ban ID": ""}]
    match_list_0_20 = [{"name_match": "Moins de 20%", "Ban ID": ""}]

    for erp in erp_list:
        nom_al = erp["nom"]
        ban_id = erp["ban_id"]
        venue = mapping.get(ban_id, None)
        if venue and ban_id and venue["Venue ID"] not in venue_ids:
            venue_as_dict = {
                "Venue ID": venue["Venue ID"],
                "ERP ID AccesLibre": erp["uuid"],
                "Nom PC": venue["Venue Name"],
                "Nom AccesLibre": erp["nom"],
                "Ban ID": ban_id,
                "Adresse PC": f"{venue['Venue Address']} {venue['Venue City']} {venue['Venue Postal Code']}",
                "Adresse AccesLibre": erp["adresse"],
                "Activite PC": venue["Venue Activity"],
                "Activite AccesLibre": erp["activite"]["nom"],
                "Last Update AccesLibre": datetime.strptime(erp["updated_at"], "%Y-%m-%dT%H:%M:%S.%f%z"),
            }
            if nom_al.lower() in venue["Venue Name"].lower() or venue["Venue Name"].lower() in nom_al.lower():
                venue_ids.add(venue["Venue ID"])
                match_list_contains.append(venue_as_dict)
                continue
            if 50 < fuzz.ratio(nom_al.lower(), venue["Venue Name"].lower()) <= 100:
                venue_ids.add(venue["Venue ID"])
                match_list_50_100.append(venue_as_dict)
            elif 35 < fuzz.ratio(nom_al.lower(), venue["Venue Name"].lower()) <= 50:
                venue_ids.add(venue["Venue ID"])
                match_list_35_50.append(venue_as_dict)
            elif 20 < fuzz.ratio(nom_al.lower(), venue["Venue Name"].lower()) <= 35:
                venue_ids.add(venue["Venue ID"])
                match_list_20_35.append(venue_as_dict)
            elif fuzz.ratio(nom_al.lower(), venue["Venue Name"].lower()) <= 20:
                venue_ids.add(venue["Venue ID"])
                match_list_0_20.append(venue_as_dict)
    return [
        sorted(match_list_contains, key=lambda x: x["Ban ID"]),  # type: ignore[list-item]
        sorted(match_list_50_100, key=lambda x: x["Ban ID"]),  # type: ignore[list-item]
        sorted(match_list_35_50, key=lambda x: x["Ban ID"]),  # type: ignore[list-item]
        sorted(match_list_20_35, key=lambda x: x["Ban ID"]),  # type: ignore[list-item]
        sorted(match_list_0_20, key=lambda x: x["Ban ID"]),  # type: ignore[list-item]
    ]


def export_match_as_csv(match: list, filename: pathlib.Path) -> None:
    result_file = PATH / filename
    with open(result_file, "w", newline="", encoding="utf-8") as csv_file:
        headers = [
            "name_match",
            "Venue ID",
            "ERP ID AccesLibre",
            "Nom PC",
            "Nom AccesLibre",
            "Ban ID",
            "Adresse PC",
            "Adresse AccesLibre",
            "Activite PC",
            "Activite AccesLibre",
            "Last Update AccesLibre",
        ]
        empty_row = {
            "name_match": "",
            "Venue ID": "",
            "ERP ID AccesLibre": "",
            "Nom PC": "",
            "Nom AccesLibre": "",
            "Ban ID": "",
            "Adresse PC": "",
            "Adresse AccesLibre": "",
            "Activite PC": "",
            "Activite AccesLibre": "",
            "Last Update AccesLibre": "",
        }
        writer = csv.DictWriter(csv_file, fieldnames=headers)

        writer.writeheader()
        for match_list in match:
            writer.writerows(match_list)
            writer.writerow(empty_row)

    print(f"Exportation des données dans {filename} terminée.")


def main() -> None:
    now = datetime.utcnow().strftime("%Y%m%d-%H%M")
    pc_venue_file = PATH / "data/pc_permanent_venues.json"
    acceslibre_file = PATH / "data/acceslibre_all.json"

    # Request API if file doesn't exist yet
    if not os.path.exists(acceslibre_file):
        print("requesting API")
        request_acceslibre_api_and_save_output(acceslibre_file)
        merge_acceslibre_json_files()
        remove_duplication(acceslibre_file)
    # Save our data into a JSON file if file doesn't exist yet
    if not os.path.exists(pc_venue_file):
        print("save permanent venues in json file")
        save_permanent_venues_in_json(pc_venue_file)
    match_list = find_match(pc_venue_file, acceslibre_file)
    print(f"{len(match_list)} match found")
    export_match_filename = PATH / f"match_all_{now}.csv"
    export_match_as_csv(match_list, export_match_filename)


if __name__ == "__main__":
    main()
