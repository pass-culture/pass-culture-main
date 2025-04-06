from enum import Enum

from pcapi.core.categories import pro_categories
from pcapi.core.categories.models import EacFormat
from pcapi.core.categories.models import ExtraDataFieldEnum
from pcapi.core.categories.models import FieldCondition
from pcapi.core.categories.models import HomepageLabels
from pcapi.core.categories.models import OnlineOfflinePlatformChoices
from pcapi.core.categories.models import ReimbursementRuleChoices
from pcapi.core.categories.models import Subcategory


# region Subcategories declarations
# region FILM
SUPPORT_PHYSIQUE_FILM = Subcategory(
    id="SUPPORT_PHYSIQUE_FILM",
    category=pro_categories.FILM,
    pro_label="Support physique (DVD, Blu-ray...)",
    app_label="Support physique (DVD, Blu-ray...)",
    homepage_label_name=HomepageLabels.FILMS.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
ABO_MEDIATHEQUE = Subcategory(
    id="ABO_MEDIATHEQUE",
    category=pro_categories.FILM,
    pro_label="Abonnement médiathèque",
    app_label="Abonnement médiathèque",
    homepage_label_name=HomepageLabels.FILMS.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
VOD = Subcategory(
    id="VOD",
    category=pro_categories.FILM,
    pro_label="Vidéo à la demande",
    app_label="Vidéo à la demande",
    homepage_label_name=HomepageLabels.FILMS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
ABO_PLATEFORME_VIDEO = Subcategory(
    id="ABO_PLATEFORME_VIDEO",
    category=pro_categories.FILM,
    pro_label="Abonnement plateforme streaming",
    app_label="Abonnement plateforme streaming",
    homepage_label_name=HomepageLabels.FILMS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
AUTRE_SUPPORT_NUMERIQUE = Subcategory(
    id="AUTRE_SUPPORT_NUMERIQUE",
    category=pro_categories.FILM,
    pro_label="Autre support numérique",
    app_label="Autre support numérique",
    homepage_label_name=HomepageLabels.FILMS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
# endregion
# region CINEMA
CARTE_CINE_MULTISEANCES = Subcategory(
    id="CARTE_CINE_MULTISEANCES",
    category=pro_categories.CINEMA,
    pro_label="Carte cinéma multi-séances",
    app_label="Carte cinéma multi-séances",
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
CARTE_CINE_ILLIMITE = Subcategory(
    id="CARTE_CINE_ILLIMITE",
    category=pro_categories.CINEMA,
    pro_label="Carte cinéma illimité",
    app_label="Carte cinéma illimité",
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
SEANCE_CINE = Subcategory(
    id="SEANCE_CINE",
    category=pro_categories.CINEMA,
    pro_label="Séance de cinéma",
    app_label="Séance de cinéma",
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.VISA.value: FieldCondition(),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
)
EVENEMENT_CINE = Subcategory(
    id="EVENEMENT_CINE",
    category=pro_categories.CINEMA,
    pro_label="Évènement cinématographique",
    app_label="Évènement cinéma",
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.VISA.value: FieldCondition(),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
)
FESTIVAL_CINE = Subcategory(
    id="FESTIVAL_CINE",
    category=pro_categories.CINEMA,
    pro_label="Festival de cinéma",
    app_label="Festival de cinéma",
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.VISA.value: FieldCondition(),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    can_have_opening_hours=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.FESTIVAL_SALON_CONGRES, EacFormat.PROJECTION_AUDIOVISUELLE],
)
CINE_VENTE_DISTANCE = Subcategory(
    id="CINE_VENTE_DISTANCE",
    category=pro_categories.CINEMA,
    pro_label="Cinéma vente à distance",
    app_label="Cinéma",
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.VISA.value: FieldCondition(),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=True,
)

CINE_PLEIN_AIR = Subcategory(
    id="CINE_PLEIN_AIR",
    category=pro_categories.CINEMA,
    pro_label="Cinéma plein air",
    app_label="Cinéma plein air",
    homepage_label_name=HomepageLabels.CINEMA.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.VISA.value: FieldCondition(),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.PROJECTION_AUDIOVISUELLE],
)

# endregion
# region CONFERENCE

CONFERENCE = Subcategory(
    id="CONFERENCE",
    category=pro_categories.CONFERENCE_RENCONTRE,
    pro_label="Conférence",
    app_label="Conférence",
    homepage_label_name=HomepageLabels.RENCONTRES.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.CONFERENCE_RENCONTRE],
)
RENCONTRE = Subcategory(
    id="RENCONTRE",
    category=pro_categories.CONFERENCE_RENCONTRE,
    pro_label="Rencontre",
    app_label="Rencontre",
    homepage_label_name=HomepageLabels.RENCONTRES.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.CONFERENCE_RENCONTRE],
)
DECOUVERTE_METIERS = Subcategory(
    id="DECOUVERTE_METIERS",
    category=pro_categories.CONFERENCE_RENCONTRE,
    pro_label="Découverte des métiers",
    app_label="Découverte des métiers",
    homepage_label_name=HomepageLabels.RENCONTRES.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_selectable=False,
)
SALON = Subcategory(
    id="SALON",
    category=pro_categories.CONFERENCE_RENCONTRE,
    pro_label="Salon, Convention",
    app_label="Salon, Convention",
    homepage_label_name=HomepageLabels.RENCONTRES.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    can_have_opening_hours=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.FESTIVAL_SALON_CONGRES],
)
RENCONTRE_EN_LIGNE = Subcategory(
    id="RENCONTRE_EN_LIGNE",
    category=pro_categories.CONFERENCE_RENCONTRE,
    pro_label="Rencontre en ligne",
    app_label="Rencontre en ligne",
    homepage_label_name=HomepageLabels.RENCONTRES.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
    formats=[EacFormat.CONFERENCE_RENCONTRE],
)
# endregion
# region JEU
CONCOURS = Subcategory(
    id="CONCOURS",
    category=pro_categories.JEU,
    pro_label="Concours - jeux",
    app_label="Concours - jeux",
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
RENCONTRE_JEU = Subcategory(
    id="RENCONTRE_JEU",
    category=pro_categories.JEU,
    pro_label="Rencontres - jeux",
    app_label="Rencontres - jeux",
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
ESCAPE_GAME = Subcategory(
    id="ESCAPE_GAME",
    category=pro_categories.JEU,
    pro_label="Escape game",
    app_label="Escape game",
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
EVENEMENT_JEU = Subcategory(
    id="EVENEMENT_JEU",
    category=pro_categories.JEU,
    pro_label="Évènements - jeux",
    app_label="Évènements - jeux",
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
JEU_EN_LIGNE = Subcategory(
    id="JEU_EN_LIGNE",
    category=pro_categories.JEU,
    pro_label="Jeux en ligne",
    app_label="Jeux en ligne",
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_free=False,
    is_bookable_by_underage_when_not_free=False,
)
ABO_JEU_VIDEO = Subcategory(
    id="ABO_JEU_VIDEO",
    category=pro_categories.JEU,
    pro_label="Abonnement jeux vidéos",
    app_label="Abonnement jeux vidéos",
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_free=False,
    is_bookable_by_underage_when_not_free=False,
)
ABO_LUDOTHEQUE = Subcategory(
    id="ABO_LUDOTHEQUE",
    category=pro_categories.JEU,
    pro_label="Abonnement ludothèque",
    app_label="Abonnement ludothèque",
    homepage_label_name=HomepageLabels.JEUX.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_selectable=False,
    is_bookable_by_underage_when_free=False,
    is_bookable_by_underage_when_not_free=False,
)
# endregion
# region LIVRE

LIVRE_PAPIER = Subcategory(
    id="LIVRE_PAPIER",
    category=pro_categories.LIVRE,
    pro_label="Livre papier",
    app_label="Livre",
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.BOOK.value,
)
LIVRE_NUMERIQUE = Subcategory(
    id="LIVRE_NUMERIQUE",
    category=pro_categories.LIVRE,
    pro_label="Livre numérique, e-book",
    app_label="Livre numérique, e-book",
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.BOOK.value,
    is_bookable_by_underage_when_not_free=True,
)
TELECHARGEMENT_LIVRE_AUDIO = Subcategory(
    id="TELECHARGEMENT_LIVRE_AUDIO",
    category=pro_categories.LIVRE,
    pro_label="Livre audio à télécharger",
    app_label="Livre audio à télécharger",
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=True,
)
LIVRE_AUDIO_PHYSIQUE = Subcategory(
    id="LIVRE_AUDIO_PHYSIQUE",
    category=pro_categories.LIVRE,
    pro_label="Livre audio sur support physique",
    app_label="Livre audio sur support physique",
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=True,
)
ABO_BIBLIOTHEQUE = Subcategory(
    id="ABO_BIBLIOTHEQUE",
    category=pro_categories.LIVRE,
    pro_label="Abonnement (bibliothèques, médiathèques...)",
    app_label="Abonnement (bibliothèques, médiathèques...)",
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
ABO_LIVRE_NUMERIQUE = Subcategory(
    id="ABO_LIVRE_NUMERIQUE",
    category=pro_categories.LIVRE,
    pro_label="Abonnement livres numériques",
    app_label="Abonnement livres numériques",
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.BOOK.value,
    is_bookable_by_underage_when_not_free=True,
)
FESTIVAL_LIVRE = Subcategory(
    id="FESTIVAL_LIVRE",
    category=pro_categories.LIVRE,
    pro_label="Festival et salon du livre",
    app_label="Festival et salon du livre",
    homepage_label_name=HomepageLabels.LIVRES.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=False,
    can_have_opening_hours=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
CARTE_JEUNES = Subcategory(
    id="CARTE_JEUNES",
    category=pro_categories.CARTE_JEUNES,
    pro_label="Carte jeunes",
    app_label="Carte jeunes",
    homepage_label_name=HomepageLabels.CARTE_JEUNES.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=True,
)
# endregion
# region VISITE

CARTE_MUSEE = Subcategory(
    id="CARTE_MUSEE",
    category=pro_categories.MUSEE,
    pro_label="Abonnement musée, carte ou pass",
    app_label="Abonnement musée, carte ou pass",
    homepage_label_name=HomepageLabels.MUSEE.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=True,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)

VISITE = Subcategory(
    id="VISITE",
    category=pro_categories.MUSEE,
    pro_label="Visite",
    app_label="Visite",
    homepage_label_name=HomepageLabels.VISITES.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    can_have_opening_hours=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.VISITE_LIBRE],
)
VISITE_GUIDEE = Subcategory(
    id="VISITE_GUIDEE",
    category=pro_categories.MUSEE,
    pro_label="Visite guidée",
    app_label="Visite guidée",
    homepage_label_name=HomepageLabels.VISITES.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.VISITE_GUIDEE],
)
EVENEMENT_PATRIMOINE = Subcategory(
    id="EVENEMENT_PATRIMOINE",
    category=pro_categories.MUSEE,
    pro_label="Évènement et atelier patrimoine",
    app_label="Évènement et atelier patrimoine",
    homepage_label_name=HomepageLabels.VISITES.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
VISITE_VIRTUELLE = Subcategory(
    id="VISITE_VIRTUELLE",
    category=pro_categories.MUSEE,
    pro_label="Visite virtuelle",
    app_label="Visite virtuelle",
    homepage_label_name=HomepageLabels.VISITES.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
MUSEE_VENTE_DISTANCE = Subcategory(
    id="MUSEE_VENTE_DISTANCE",
    category=pro_categories.MUSEE,
    pro_label="Musée vente à distance",
    app_label="Musée vente à distance",
    homepage_label_name=HomepageLabels.MUSEE.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=True,
)
FESTIVAL_ART_VISUEL = Subcategory(
    id="FESTIVAL_ART_VISUEL",
    category=pro_categories.MUSEE,
    pro_label="Festival d'arts visuels / arts numériques",
    app_label="Festival d'arts visuels / arts numériques",
    homepage_label_name=HomepageLabels.FESTIVAL.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    can_have_opening_hours=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.FESTIVAL_SALON_CONGRES],
)
# endregion
# region MUSIQUE_LIVE

CONCERT = Subcategory(
    id="CONCERT",
    category=pro_categories.MUSIQUE_LIVE,
    pro_label="Concert",
    app_label="Concert",
    homepage_label_name=HomepageLabels.CONCERT.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.CONCERT],
)
EVENEMENT_MUSIQUE = Subcategory(
    id="EVENEMENT_MUSIQUE",
    category=pro_categories.MUSIQUE_LIVE,
    pro_label="Autre type d'évènement musical",
    app_label="Autre type d'évènement musical",
    homepage_label_name=HomepageLabels.CONCERT.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.CONCERT],
)
LIVESTREAM_MUSIQUE = Subcategory(
    id="LIVESTREAM_MUSIQUE",
    category=pro_categories.MUSIQUE_LIVE,
    pro_label="Livestream musical",
    app_label="Livestream musical",
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=False,
)
ABO_CONCERT = Subcategory(
    id="ABO_CONCERT",
    category=pro_categories.MUSIQUE_LIVE,
    pro_label="Abonnement concert",
    app_label="Abonnement concert",
    homepage_label_name=HomepageLabels.CONCERT.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
FESTIVAL_MUSIQUE = Subcategory(
    id="FESTIVAL_MUSIQUE",
    category=pro_categories.MUSIQUE_LIVE,
    pro_label="Festival de musique",
    app_label="Festival de musique",
    homepage_label_name=HomepageLabels.FESTIVAL.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    can_have_opening_hours=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.FESTIVAL_SALON_CONGRES, EacFormat.CONCERT],
)
# endregion
# region MUSIQUE_ENREGISTREE
SUPPORT_PHYSIQUE_MUSIQUE_CD = Subcategory(
    id="SUPPORT_PHYSIQUE_MUSIQUE_CD",
    category=pro_categories.MUSIQUE_ENREGISTREE,
    pro_label="CD",
    app_label="CD",
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
SUPPORT_PHYSIQUE_MUSIQUE_VINYLE = Subcategory(
    id="SUPPORT_PHYSIQUE_MUSIQUE_VINYLE",
    category=pro_categories.MUSIQUE_ENREGISTREE,
    pro_label="Vinyles et autres supports",
    app_label="Vinyles et autres supports",
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
TELECHARGEMENT_MUSIQUE = Subcategory(
    id="TELECHARGEMENT_MUSIQUE",
    category=pro_categories.MUSIQUE_ENREGISTREE,
    pro_label="Téléchargement de musique",
    app_label="Téléchargement de musique",
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
        ExtraDataFieldEnum.EAN.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
ABO_PLATEFORME_MUSIQUE = Subcategory(
    id="ABO_PLATEFORME_MUSIQUE",
    category=pro_categories.MUSIQUE_ENREGISTREE,
    pro_label="Abonnement plateforme musicale",
    app_label="Abonnement plateforme musicale",
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
CAPTATION_MUSIQUE = Subcategory(
    id="CAPTATION_MUSIQUE",
    category=pro_categories.MUSIQUE_ENREGISTREE,
    pro_label="Captation musicale",
    app_label="Captation musicale",
    homepage_label_name=HomepageLabels.MUSIQUE.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.MUSIC_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.MUSIC_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.GTL_ID.value: FieldCondition(
            is_required_in_external_form=False, is_required_in_internal_form=False
        ),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_selectable=False,
)

# endregion
# region PRATIQUE
SEANCE_ESSAI_PRATIQUE_ART = Subcategory(
    id="SEANCE_ESSAI_PRATIQUE_ART",
    category=pro_categories.PRATIQUE_ART,
    pro_label="Séance d'essai",
    app_label="Séance d'essai",
    homepage_label_name=HomepageLabels.STAGE_ATELIER.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=True,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
ATELIER_PRATIQUE_ART = Subcategory(
    id="ATELIER_PRATIQUE_ART",
    category=pro_categories.PRATIQUE_ART,
    pro_label="Atelier, stage de pratique artistique",
    app_label="Atelier, stage de pratique artistique",
    homepage_label_name=HomepageLabels.STAGE_ATELIER.name,
    is_event=True,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    formats=[EacFormat.ATELIER_DE_PRATIQUE],
)
ABO_PRATIQUE_ART = Subcategory(
    id="ABO_PRATIQUE_ART",
    category=pro_categories.PRATIQUE_ART,
    pro_label="Abonnement pratique artistique",
    app_label="Abonnement pratique artistique",
    homepage_label_name=HomepageLabels.COURS.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
PRATIQUE_ART_VENTE_DISTANCE = Subcategory(
    id="PRATIQUE_ART_VENTE_DISTANCE",
    category=pro_categories.PRATIQUE_ART,
    pro_label="Pratique artistique - vente à distance",
    app_label="Pratique artistique - vente à distance",
    homepage_label_name=HomepageLabels.COURS.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.SPEAKER.value: FieldCondition()},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
PLATEFORME_PRATIQUE_ARTISTIQUE = Subcategory(
    id="PLATEFORME_PRATIQUE_ARTISTIQUE",
    category=pro_categories.PRATIQUE_ART,
    pro_label="Pratique artistique - plateforme en ligne",
    app_label="Plateforme de pratique artistique",
    homepage_label_name=HomepageLabels.PLATEFORME.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
LIVESTREAM_PRATIQUE_ARTISTIQUE = Subcategory(
    id="LIVESTREAM_PRATIQUE_ARTISTIQUE",
    category=pro_categories.PRATIQUE_ART,
    pro_label="Pratique artistique - livestream",
    app_label="Pratique artistique - livestream",
    homepage_label_name=HomepageLabels.COURS.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=False,
)
# endregion
# region MEDIAS
ABO_PRESSE_EN_LIGNE = Subcategory(
    id="ABO_PRESSE_EN_LIGNE",
    category=pro_categories.MEDIA,
    pro_label="Abonnement presse en ligne",
    app_label="Abonnement presse en ligne",
    homepage_label_name=HomepageLabels.MEDIAS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=True,
)
PODCAST = Subcategory(
    id="PODCAST",
    category=pro_categories.MEDIA,
    pro_label="Podcast",
    app_label="Podcast",
    homepage_label_name=HomepageLabels.MEDIAS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=True,
)
APP_CULTURELLE = Subcategory(
    id="APP_CULTURELLE",
    category=pro_categories.MEDIA,
    pro_label="Application culturelle",
    app_label="Application culturelle",
    homepage_label_name=HomepageLabels.MEDIAS.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=True,
)
# endregion
# region SPECTACLE
SPECTACLE_REPRESENTATION = Subcategory(
    id="SPECTACLE_REPRESENTATION",
    category=pro_categories.SPECTACLE,
    pro_label="Spectacle, représentation",
    app_label="Spectacle, représentation",
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.REPRESENTATION],
)
SPECTACLE_ENREGISTRE = Subcategory(
    id="SPECTACLE_ENREGISTRE",
    category=pro_categories.SPECTACLE,
    pro_label="Spectacle enregistré",
    app_label="Spectacle enregistré",
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_bookable_by_underage_when_not_free=False,
)
LIVESTREAM_EVENEMENT = Subcategory(
    id="LIVESTREAM_EVENEMENT",
    category=pro_categories.SPECTACLE,
    pro_label="Livestream d'évènement",
    app_label="Livestream d'évènement",
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=True,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_bookable_by_underage_when_not_free=False,
)
FESTIVAL_SPECTACLE = Subcategory(
    id="FESTIVAL_SPECTACLE",
    category=pro_categories.SPECTACLE,
    pro_label="Festival de spectacle vivant",
    app_label="Festival de spectacle vivant",
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=True,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=True,
    can_be_educational=True,
    can_have_opening_hours=True,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    can_be_withdrawable=True,
    formats=[EacFormat.FESTIVAL_SALON_CONGRES, EacFormat.REPRESENTATION],
)
ABO_SPECTACLE = Subcategory(
    id="ABO_SPECTACLE",
    category=pro_categories.SPECTACLE,
    pro_label="Abonnement spectacle",
    app_label="Abonnement spectacle",
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
    },
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
SPECTACLE_VENTE_DISTANCE = Subcategory(
    id="SPECTACLE_VENTE_DISTANCE",
    category=pro_categories.SPECTACLE,
    pro_label="Spectacle vivant - vente à distance",
    app_label="Spectacle vivant - vente à distance",
    homepage_label_name=HomepageLabels.SPECTACLES.name,
    is_event=False,
    conditional_fields={
        ExtraDataFieldEnum.AUTHOR.value: FieldCondition(),
        ExtraDataFieldEnum.SHOW_SUB_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.SHOW_TYPE.value: FieldCondition(
            is_required_in_external_form=True, is_required_in_internal_form=True
        ),
        ExtraDataFieldEnum.STAGE_DIRECTOR.value: FieldCondition(),
        ExtraDataFieldEnum.PERFORMER.value: FieldCondition(),
    },
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
# endregion
# region INSTRUMENT
ACHAT_INSTRUMENT = Subcategory(
    id="ACHAT_INSTRUMENT",
    category=pro_categories.INSTRUMENT,
    pro_label="Achat instrument",
    app_label="Achat instrument",
    homepage_label_name=HomepageLabels.INSTRUMENT.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
BON_ACHAT_INSTRUMENT = Subcategory(
    id="BON_ACHAT_INSTRUMENT",
    pro_label="Bon d'achat instrument",
    category=pro_categories.INSTRUMENT,
    app_label="Bon d'achat instrument",
    homepage_label_name=HomepageLabels.INSTRUMENT.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
    is_selectable=False,
)
LOCATION_INSTRUMENT = Subcategory(
    id="LOCATION_INSTRUMENT",
    category=pro_categories.INSTRUMENT,
    pro_label="Location instrument",
    app_label="Location instrument",
    homepage_label_name=HomepageLabels.INSTRUMENT.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
PARTITION = Subcategory(
    id="PARTITION",
    category=pro_categories.INSTRUMENT,
    pro_label="Partition",
    app_label="Partition",
    homepage_label_name=HomepageLabels.INSTRUMENT.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
# endregion
# region BEAUX_ARTS
MATERIEL_ART_CREATIF = Subcategory(
    id="MATERIEL_ART_CREATIF",
    category=pro_categories.BEAUX_ARTS,
    pro_label="Matériel arts créatifs",
    app_label="Matériel arts créatifs",
    homepage_label_name=HomepageLabels.BEAUX_ARTS.name,
    is_event=False,
    conditional_fields={ExtraDataFieldEnum.EAN.value: FieldCondition(is_required_in_external_form=True)},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.STANDARD.value,
)
# endregion
# region TECHNICAL
ACTIVATION_EVENT = Subcategory(
    id="ACTIVATION_EVENT",
    category=pro_categories.TECHNIQUE,
    pro_label="Catégorie technique d'évènement d'activation ",
    app_label="Catégorie technique d'évènement d'activation ",
    homepage_label_name=HomepageLabels.NONE.name,
    is_event=True,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE_OR_OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=False,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_selectable=False,
    is_bookable_by_underage_when_not_free=False,
)
ACTIVATION_THING = Subcategory(
    id="ACTIVATION_THING",
    category=pro_categories.TECHNIQUE,
    pro_label="Catégorie technique de thing d'activation",
    app_label="Catégorie technique de thing d'activation",
    homepage_label_name=HomepageLabels.NONE.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE_OR_OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_selectable=False,
    is_bookable_by_underage_when_not_free=False,
)
JEU_SUPPORT_PHYSIQUE = Subcategory(
    id="JEU_SUPPORT_PHYSIQUE",
    category=pro_categories.TECHNIQUE,
    pro_label="Catégorie technique Jeu support physique",
    app_label="Catégorie technique Jeu support physique",
    homepage_label_name=HomepageLabels.NONE.name,
    is_event=False,
    conditional_fields={},
    can_expire=False,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE_OR_OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_selectable=False,
    is_bookable_by_underage_when_free=False,
    is_bookable_by_underage_when_not_free=False,
)
OEUVRE_ART = Subcategory(
    id="OEUVRE_ART",
    category=pro_categories.TECHNIQUE,
    pro_label="Catégorie technique d'oeuvre d'art",
    app_label="Catégorie technique d'oeuvre d'art",
    homepage_label_name=HomepageLabels.NONE.name,
    is_event=False,
    conditional_fields={},
    can_expire=True,
    can_be_duo=False,
    can_be_educational=False,
    online_offline_platform=OnlineOfflinePlatformChoices.ONLINE_OR_OFFLINE.value,
    is_digital_deposit=False,
    is_physical_deposit=True,
    reimbursement_rule=ReimbursementRuleChoices.NOT_REIMBURSED.value,
    is_selectable=False,
    is_bookable_by_underage_when_not_free=False,
)
# endregion
# endregion

ALL_SUBCATEGORIES = (
    ABO_BIBLIOTHEQUE,
    ABO_CONCERT,
    ABO_JEU_VIDEO,
    ABO_LIVRE_NUMERIQUE,
    ABO_LUDOTHEQUE,
    ABO_MEDIATHEQUE,
    ABO_PLATEFORME_MUSIQUE,
    ABO_PLATEFORME_VIDEO,
    ABO_PRATIQUE_ART,
    ABO_PRESSE_EN_LIGNE,
    ABO_SPECTACLE,
    ACHAT_INSTRUMENT,
    ACTIVATION_EVENT,
    ACTIVATION_THING,
    APP_CULTURELLE,
    ATELIER_PRATIQUE_ART,
    AUTRE_SUPPORT_NUMERIQUE,
    BON_ACHAT_INSTRUMENT,
    CAPTATION_MUSIQUE,
    CARTE_CINE_ILLIMITE,
    CARTE_CINE_MULTISEANCES,
    CARTE_JEUNES,
    CARTE_MUSEE,
    CINE_PLEIN_AIR,
    CINE_VENTE_DISTANCE,
    CONCERT,
    CONCOURS,
    CONFERENCE,
    DECOUVERTE_METIERS,
    ESCAPE_GAME,
    EVENEMENT_CINE,
    EVENEMENT_JEU,
    EVENEMENT_MUSIQUE,
    EVENEMENT_PATRIMOINE,
    FESTIVAL_ART_VISUEL,
    FESTIVAL_CINE,
    FESTIVAL_LIVRE,
    FESTIVAL_MUSIQUE,
    FESTIVAL_SPECTACLE,
    JEU_EN_LIGNE,
    JEU_SUPPORT_PHYSIQUE,
    LIVESTREAM_EVENEMENT,
    LIVESTREAM_MUSIQUE,
    LIVESTREAM_PRATIQUE_ARTISTIQUE,
    LIVRE_AUDIO_PHYSIQUE,
    LIVRE_NUMERIQUE,
    LIVRE_PAPIER,
    LOCATION_INSTRUMENT,
    MATERIEL_ART_CREATIF,
    MUSEE_VENTE_DISTANCE,
    OEUVRE_ART,
    PARTITION,
    PLATEFORME_PRATIQUE_ARTISTIQUE,
    PRATIQUE_ART_VENTE_DISTANCE,
    PODCAST,
    RENCONTRE_EN_LIGNE,
    RENCONTRE_JEU,
    RENCONTRE,
    SALON,
    SEANCE_CINE,
    SEANCE_ESSAI_PRATIQUE_ART,
    SPECTACLE_ENREGISTRE,
    SPECTACLE_REPRESENTATION,
    SPECTACLE_VENTE_DISTANCE,
    SUPPORT_PHYSIQUE_FILM,
    SUPPORT_PHYSIQUE_MUSIQUE_CD,
    SUPPORT_PHYSIQUE_MUSIQUE_VINYLE,
    TELECHARGEMENT_LIVRE_AUDIO,
    TELECHARGEMENT_MUSIQUE,
    VISITE_GUIDEE,
    VISITE_VIRTUELLE,
    VISITE,
    VOD,
)
ALL_SUBCATEGORIES_DICT = {subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES}
PERMANENT_SUBCATEGORIES = {
    subcategory.id: subcategory
    for subcategory in ALL_SUBCATEGORIES
    if not subcategory.can_expire and not subcategory.is_event
}
EXPIRABLE_SUBCATEGORIES = {subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.can_expire}
EVENT_SUBCATEGORIES = {subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.is_event}
ACTIVATION_SUBCATEGORIES = (ACTIVATION_EVENT.id, ACTIVATION_THING.id)
BOOK_WITH_EAN = (LIVRE_PAPIER.id, LIVRE_AUDIO_PHYSIQUE.id, LIVRE_NUMERIQUE.id)

COLLECTIVE_SUBCATEGORIES = {
    subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.can_be_educational
}

WITHDRAWABLE_SUBCATEGORIES = {
    subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.can_be_withdrawable
}

EVENT_WITH_OPENING_HOURS_SUBCATEGORIES = {
    subcategory.id: subcategory for subcategory in ALL_SUBCATEGORIES if subcategory.can_have_opening_hours
}

MUSIC_SUBCATEGORIES = {
    subcategory.id: subcategory
    for subcategory in ALL_SUBCATEGORIES
    if subcategory.category in [pro_categories.MUSIQUE_LIVE, pro_categories.MUSIQUE_ENREGISTREE]
}

# WARNING: You will need to regenerate offer_music_subcategory_with_gtl_id_substr_idx when adding a subcategory to MUSIC_TITELIVE_SEARCH_SUBCATEGORY_IDS
MUSIC_TITELIVE_SUBCATEGORY_SEARCH_IDS = {
    subcategory.id for subcategory in [SUPPORT_PHYSIQUE_MUSIQUE_CD, SUPPORT_PHYSIQUE_MUSIQUE_VINYLE]
}


assert set(subcategory.id for subcategory in ALL_SUBCATEGORIES) == set(
    subcategory.id for subcategory in locals().values() if isinstance(subcategory, Subcategory)
)

SubcategoryProLabelEnum = Enum("SubcategoryProLabelEnum", {subcategory.id: subcategory.pro_label for subcategory in ALL_SUBCATEGORIES})  # type: ignore[misc]
OnlineOfflinePlatformChoicesEnum = Enum(  # type: ignore[misc]
    "OnlineOfflinePlatformChoicesEnum",
    {choice: choice for choice in [c.value for c in OnlineOfflinePlatformChoices]},
)

SubcategoryIdEnum = Enum("SubcategoryIdEnum", {subcategory.id: subcategory.id for subcategory in ALL_SUBCATEGORIES})  # type: ignore[misc]
