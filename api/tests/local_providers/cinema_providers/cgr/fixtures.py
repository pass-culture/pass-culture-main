import json
from typing import Dict
from typing import List


def cgr_response_template(films_info: List[Dict]) -> str:
    return f"""
       <?xml version="1.0" encoding="UTF-8"?>
        <SOAP-ENV:Envelope
            xmlns:xsd="http://www.w3.org/2001/XMLSchema"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
            <SOAP-ENV:Header/>
            <SOAP-ENV:Body>
                <ns1:GetSeancesPassCultureResponse xmlns:ns1="urn:GestionCinemaWS">
                    <GetSeancesPassCultureResult>
                        {json.dumps({
                            "CodeErreur": 0,
                            "IntituleErreur": "",
                            "ObjetRetour": {
                                "NumCine": 999,
                                "Films": film(films_info),
                            },
                        })}
                    </GetSeancesPassCultureResult>
                </ns1:GetSeancesPassCultureResponse>
            </SOAP-ENV:Body>
        </SOAP-ENV:Envelope>
        """.strip()


def film(films_info: List[Dict]) -> List[Dict]:
    return [
        {
            "IDFilm": film_info["IDFilm"],
            "IDFilmAlloCine": film_info["IDFilmAlloCine"],
            "Titre": film_info["Titre"],
            "NumVisa": film_info["NumVisa"],
            "Duree": film_info["Duree"],
            "Synopsis": film_info["Synopsis"],
            "Affiche": film_info["Affiche"],
            "TypeFilm": film_info["TypeFilm"],
            "Seances": film_info["Seances"],
        }
        for film_info in films_info
    ]


SEANCE_177182 = {
    "IDSeance": 177182,
    "Date": "2023-01-29",
    "Heure": "14:00:00.000",
    "NbPlacesRestantes": 99,
    "bAvecPlacement": True,
    "bAvecDuo": True,
    "bICE": True,
    "Relief": "2D",
    "Version": "VF",
    "bAVP": False,
    "PrixUnitaire": 11,
}

FILM_138473 = {
    "IDFilm": 138473,
    "IDFilmAlloCine": 138473,
    "Titre": "Venom",
    "NumVisa": 149341,
    "Duree": 112,
    "Synopsis": "Possédé par un symbiote qui agit de manière autonome, le journaliste Eddie Brock devient le protecteur létal Venom.",
    "Affiche": "https://example.com/149341.jpg",
    "TypeFilm": "CNC",
    "Seances": [SEANCE_177182],
}

SEANCE_182019 = {
    "IDSeance": 182019,
    "Date": "2023-03-04",
    "Heure": "16:00:00.000",
    "NbPlacesRestantes": 168,
    "bAvecPlacement": True,
    "bAvecDuo": True,
    "bICE": True,
    "Relief": "2D",
    "Version": "VF",
    "bAVP": False,
    "PrixUnitaire": 11,
}

FILM_234099 = {
    "IDFilm": 234099,
    "IDFilmAlloCine": 234099,
    "Titre": "Super Mario Bros, Le Film",
    "NumVisa": 82382,
    "Duree": 92,
    "Synopsis": "Un film basé sur l'univers du célèbre jeu : Super Mario Bros.",
    "Affiche": "https://example.com/82382.jpg",
    "TypeFilm": "CNC",
    "Seances": [SEANCE_182019],
}
