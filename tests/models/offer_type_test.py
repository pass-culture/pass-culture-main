from pcapi.models.offer_type import Category


def test_category_enum_content():
    category_dict = {c.name: c.value for c in Category}
    assert category_dict == {
        "CINEMA": [
            "Carte cinéma illimité",
            "Carte cinéma multi-séances",
            "Cinéma plein air",
            "Cinéma",
            "Événement cinéma",
            "Festival de cinéma",
            "Séance de cinéma",
        ],
        "CONFERENCE": ["Conférence", "Découverte des métiers", "Rencontre en ligne", "Rencontre", "Salon, Convention"],
        "FILM": [
            "Abonnement médiathèque",
            "Abonnement plateforme streaming",
            "Autre support numérique",
            "Support physique (DVD, Blu-ray...)",
            "Vidéo à la demande",
        ],
        "INSTRUMENT": ["Achat instrument", "Bon d'achat instrument", "Location instrument", "Partition"],
        "JEUX_VIDEO": [
            "Abonnement jeux vidéos",
            "Abonnement ludothèque",
            "Concours - jeux",
            "Escape game",
            "Événements - jeux",
            "Jeux en ligne",
            "Rencontres - jeux",
        ],
        "LECON": ["Abonnement pratique artistique", "Atelier, stage de pratique artistique", "Séance d'essai"],
        "LIVRE": [
            "Abonnement (bibliothèques, médiathèques...)",
            "Abonnement livres numériques",
            "Festival et salon du livre",
            "Livre audio sur support physique",
            "Livre numérique, e-book",
            "Livre",
            "Livre audio à télécharger",
        ],
        "MATERIEL_ART_CREA": ["Matériel arts créatifs"],
        "MUSIQUE": [
            "Abonnement concert",
            "Abonnement plateforme musicale",
            "Captation musicale",
            "Concert",
            "Autre type d'événement musical",
            "Festival de musique",
            "Live stream musical",
            "Support physique (CD, vinyle...)",
            "Téléchargement de musique",
        ],
        "PRESSE": ["Abonnement presse en ligne", "Application culturelle", "Podcast"],
        "SPECTACLE": [
            "Abonnement spectacle",
            "Festival",
            "Live stream d'événement",
            "Spectacle enregistré",
            "Spectacle, représentation",
        ],
        "VISITE": [
            "Entrée libre ou abonnement musée",
            "Cartes musées, patrimoine...",
            "Événement et atelier patrimoine",
            "Musée vente à distance",
            "Visite guidée",
            "Visite virtuelle",
            "Visite",
        ],
    }
