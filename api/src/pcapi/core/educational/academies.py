ACADEMIES = {
    "Amiens": ["02", "60", "80"],
    "Aix-Marseille": ["04", "05", "13", "84"],
    "Besançon": ["25", "39", "70", "90"],
    "Bordeaux": ["24", "33", "40", "47", "64"],
    "Clermont-Ferrand": ["03", "15", "43", "63"],
    "Corse": ["2A", "2B"],
    "Créteil": ["77", "93", "94"],
    "Dijon": ["21", "58", "71", "89"],
    "Grenoble": ["07", "26", "38", "73", "74"],
    "Guadeloupe": ["971", "977", "978"],
    "Guyane": ["973"],
    "La Réunion": ["974"],
    "Lille": ["59", "62"],
    "Limoges": ["19", "23", "87"],
    "Lyon": ["01", "42", "69"],
    "Martinique": ["972"],
    "Mayotte": ["976"],
    "Montpellier": ["11", "30", "34", "48", "66"],
    "Nancy-Metz": ["54", "55", "57", "88"],
    "Nantes": ["44", "49", "53", "72", "85"],
    "Nice": ["06", "83"],
    "Normandie": ["14", "50", "61", "27", "76", "975"],
    "Orléans-Tours": ["18", "28", "36", "37", "41", "45"],
    "Paris": ["75"],
    "Poitiers": ["16", "17", "79", "86"],
    "Reims": ["08", "10", "51", "52"],
    "Rennes": ["22", "29", "35", "56"],
    "Strasbourg": ["67", "68"],
    "Toulouse": ["09", "12", "31", "32", "46", "65", "81", "82"],
    "Versailles": ["78", "91", "92", "95"],
}


DEPARTMENT_TO_ACADEMIES = {
    department: academy for academy, departments in ACADEMIES.items() for department in departments
}


def get_academy_from_department(code: str) -> str:
    return DEPARTMENT_TO_ACADEMIES[code]
