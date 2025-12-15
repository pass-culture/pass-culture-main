from pcapi.core.categories import subcategories


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
THINGS_WITH_EAN = {
    subcategories.LIVRE_PAPIER.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_CD.id,
    subcategories.SUPPORT_PHYSIQUE_MUSIQUE_VINYLE.id,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
THINGS_RANDOM = {
    subcategories.ABO_BIBLIOTHEQUE.id,
    subcategories.ABO_CONCERT.id,
    subcategories.ABO_MEDIATHEQUE.id,
    subcategories.ABO_PRATIQUE_ART.id,
    subcategories.ACHAT_INSTRUMENT.id,
    subcategories.CARTE_CINE_ILLIMITE.id,
    subcategories.CARTE_CINE_MULTISEANCES.id,
    subcategories.CARTE_JEUNES.id,
    subcategories.CARTE_MUSEE.id,
    subcategories.ESCAPE_GAME.id,
    subcategories.LIVRE_AUDIO_PHYSIQUE.id,
    subcategories.LOCATION_INSTRUMENT.id,
    subcategories.MATERIEL_ART_CREATIF.id,
    subcategories.PARTITION.id,
    subcategories.SUPPORT_PHYSIQUE_FILM.id,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
DIGITAL_THING = {
    subcategories.TELECHARGEMENT_MUSIQUE.id,
    subcategories.LIVRE_NUMERIQUE.id,
    subcategories.PLATEFORME_PRATIQUE_ARTISTIQUE.id,
    subcategories.AUTRE_SUPPORT_NUMERIQUE.id,
    subcategories.MUSEE_VENTE_DISTANCE.id,
    subcategories.VISITE_VIRTUELLE.id,
    subcategories.PRATIQUE_ART_VENTE_DISTANCE.id,
    subcategories.ABO_PLATEFORME_VIDEO.id,
    subcategories.ABO_PRESSE_EN_LIGNE.id,
    subcategories.APP_CULTURELLE.id,
    subcategories.JEU_EN_LIGNE.id,
    subcategories.CINE_VENTE_DISTANCE.id,
    subcategories.ABO_LIVRE_NUMERIQUE.id,
    subcategories.ABO_JEU_VIDEO.id,
    subcategories.PODCAST.id,
    subcategories.TELECHARGEMENT_LIVRE_AUDIO.id,
    subcategories.ABO_PLATEFORME_MUSIQUE.id,
    subcategories.VOD.id,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
DIGITAL_ACTIVITY = {
    subcategories.SPECTACLE_ENREGISTRE.id,
    subcategories.SPECTACLE_VENTE_DISTANCE.id,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
CANNOT_BE_CREATED = {
    subcategories.ACTIVATION_EVENT.id,
    subcategories.CAPTATION_MUSIQUE.id,
    subcategories.OEUVRE_ART.id,
    subcategories.BON_ACHAT_INSTRUMENT.id,
    subcategories.ACTIVATION_THING.id,
    subcategories.ABO_LUDOTHEQUE.id,
    subcategories.JEU_SUPPORT_PHYSIQUE.id,
    subcategories.DECOUVERTE_METIERS.id,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
ACTIVITY_SUBSCRIPTION = {
    subcategories.ABO_SPECTACLE.id,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
ACTIVITY_ONLINE = {
    subcategories.LIVESTREAM_MUSIQUE.id,
    subcategories.RENCONTRE_EN_LIGNE.id,
    subcategories.LIVESTREAM_PRATIQUE_ARTISTIQUE.id,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
ACTIVITY_ONLINE_EVENT = {
    subcategories.LIVESTREAM_EVENEMENT.id,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
ACTIVITY_WITHDRAWABLE = {
    subcategories.SPECTACLE_REPRESENTATION.id,
    subcategories.FESTIVAL_SPECTACLE.id,
    subcategories.FESTIVAL_ART_VISUEL.id,
    subcategories.CONCERT.id,
    subcategories.FESTIVAL_MUSIQUE.id,
    subcategories.EVENEMENT_MUSIQUE.id,
}


# TODO(jbaudet - 12/2025): warning: this might not be accurate
# delete this TODO if nothing has changed in a couple of months
ACTIVITY_RANDOM = {
    subcategories.ATELIER_PRATIQUE_ART.id,
    subcategories.CINE_PLEIN_AIR.id,
    subcategories.CONCOURS.id,
    subcategories.CONFERENCE.id,
    subcategories.EVENEMENT_CINE.id,
    subcategories.EVENEMENT_JEU.id,
    subcategories.EVENEMENT_PATRIMOINE.id,
    subcategories.FESTIVAL_CINE.id,
    subcategories.FESTIVAL_LIVRE.id,
    subcategories.RENCONTRE.id,
    subcategories.RENCONTRE_JEU.id,
    subcategories.SALON.id,
    subcategories.SEANCE_CINE.id,
    subcategories.SEANCE_ESSAI_PRATIQUE_ART.id,
    subcategories.VISITE_LIBRE.id,
    subcategories.VISITE_GUIDEE.id,
}


class UnknownSubcategory(Exception):
    pass


def switch(subcategory: subcategories.Subcategory) -> None:
    subcategory_id = subcategory.id

    if subcategory_id in THINGS_WITH_EAN:
        pass
    elif subcategory_id in THINGS_RANDOM:
        pass
    elif subcategory_id in DIGITAL_THING:
        pass
    elif subcategory_id in DIGITAL_ACTIVITY:
        pass
    elif subcategory_id in ACTIVITY_SUBSCRIPTION:
        pass
    elif subcategory_id in ACTIVITY_ONLINE:
        pass
    elif subcategory_id in ACTIVITY_ONLINE_EVENT:
        pass
    elif subcategory_id in ACTIVITY_WITHDRAWABLE:
        pass
    elif subcategory_id in ACTIVITY_RANDOM:
        pass
    elif subcategory_id in CANNOT_BE_CREATED:
        pass

    # should not be reachable!
    raise UnknownSubcategory(subcategory_id)
