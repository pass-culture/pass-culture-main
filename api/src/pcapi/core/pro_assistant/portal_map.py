"""Map of the pro portal pages the assistant can send users to.

This map is both:
- part of the knowledge given to the LLM (what each page is for);
- the whitelist of links the assistant is allowed to return (the LLM only
  returns `route_id`s, paths and labels are resolved here).

Paths come from `pro/src/app/AppRouter/` (routesMap.tsx, routes/*.tsx) and
`pro/src/pages/Sitemap/Sitemap.tsx`. Keep them in sync when routes change.
"""

import dataclasses
import re


@dataclasses.dataclass(frozen=True)
class PortalPage:
    route_id: str
    path: str
    title: str
    description: str
    prerequisites: str = ""
    # Other paths (with `:param` segments) that belong to this page. They are only
    # used to detect the page the user is currently on, never as link targets.
    related_paths: tuple[str, ...] = ()


PORTAL_PAGES: tuple[PortalPage, ...] = (
    PortalPage(
        route_id="home",
        path="/accueil",
        title="Accueil",
        description=(
            "Page d'accueil de l'espace partenaire pour la structure sélectionnée : statistiques de réservations, "
            "étapes restant à compléter (coordonnées bancaires, première offre…), raccourcis et actualités."
        ),
    ),
    PortalPage(
        route_id="hub",
        path="/hub",
        title="Changer de structure",
        description=(
            "Choisir la structure sur laquelle travailler quand on en gère plusieurs "
            "(menu de sélection de structure en haut de l'espace partenaire)."
        ),
    ),
    PortalPage(
        route_id="add_venue",
        path="/inscription/structure/recherche",
        title="Ajouter une structure",
        description=(
            "Ajouter une nouvelle structure (lieu, établissement) à son compte, à partir de son SIRET. "
            "Une entité juridique peut avoir plusieurs structures."
        ),
        related_paths=("/inscription/structure", "/structures/lieux/creation"),
    ),
    PortalPage(
        route_id="individual_offer_creation",
        path="/offre/individuelle/creation/description",
        title="Créer une offre individuelle",
        description=(
            "Créer une offre à destination des jeunes, visible dans l'application pass Culture (places de cinéma, "
            "concerts, spectacles, livres, disques, instruments, cours, ateliers…). Parcours étape par étape : "
            "description, informations pratiques, localisation, image et vidéo, tarifs, horaires ou stocks, "
            "récapitulatif puis publication."
        ),
        related_paths=(
            "/offre/individuelle/:offerId/creation/:step",
            "/onboarding/offre/individuelle/creation/description",
            "/onboarding/offre/individuelle/:offerId/creation/:step",
        ),
    ),
    PortalPage(
        route_id="individual_offers",
        path="/offres",
        title="Offres individuelles",
        description=(
            "Liste des offres individuelles de la structure : rechercher, filtrer par statut, modifier une offre "
            "(description, tarifs, horaires, stocks, image), la mettre en pause ou la désactiver."
        ),
        related_paths=(
            "/offre/individuelle/:offerId/edition/:step",
            "/offre/individuelle/:offerId/visibilite",
        ),
    ),
    PortalPage(
        route_id="individual_bookings",
        path="/reservations",
        title="Réservations individuelles",
        description=(
            "Consulter, filtrer et exporter les réservations faites par les jeunes sur les offres individuelles, "
            "et suivre leur statut (réservée, validée, annulée, remboursée…)."
        ),
        related_paths=("/offre/individuelle/:offerId/reservations",),
    ),
    PortalPage(
        route_id="desk",
        path="/guichet",
        title="Guichet",
        description=(
            "Saisir la contremarque (code de réservation présenté par le jeune) pour la vérifier et la valider "
            "au moment du retrait ou de l'événement, ou invalider une contremarque validée par erreur."
        ),
    ),
    PortalPage(
        route_id="individual_venue_page",
        path="/partenaire/page-partenaire",
        title="Page sur l'application",
        description=(
            "Gérer la page de la structure visible par les jeunes dans l'application pass Culture : "
            "description, image, accessibilité, horaires d'ouverture, informations de contact."
        ),
        prerequisites="Disponible lorsque la structure propose des offres individuelles.",
        related_paths=("/partenaire/page-partenaire/edition",),
    ),
    PortalPage(
        route_id="collective_offer_creation",
        path="/offre/creation",
        title="Créer une offre collective",
        description=(
            "Créer une offre à destination des groupes scolaires, visible par les enseignants sur la plateforme "
            "ADAGE. On choisit d'abord entre une offre vitrine (sans date ni prix, pour présenter une activité "
            "et recevoir des demandes) et une offre réservable (datée, avec un prix, pour un établissement donné), "
            "puis on suit le parcours : détails, dates et prix, établissement, informations pratiques, aperçu, "
            "récapitulatif."
        ),
        prerequisites="La structure doit être référencée sur ADAGE pour proposer des offres collectives.",
        related_paths=(
            "/offre/creation/collectif",
            "/offre/creation/collectif/vitrine",
            "/offre/creation/collectif/selection",
            "/offre/collectif/:offerId/creation",
            "/offre/collectif/vitrine/:offerId/creation",
            "/offre/collectif/creation/:offerId/requete/:requestId",
            "/offre/:offerId/collectif/stocks",
            "/offre/:offerId/collectif/informations-pratiques",
            "/offre/:offerId/collectif/etablissement",
            "/offre/:offerId/collectif/creation/:step",
            "/offre/:offerId/collectif/vitrine/creation/:step",
            "/offre/:offerId/collectif/confirmation",
            "/offre/:offerId/collectif/vitrine/confirmation",
        ),
    ),
    PortalPage(
        route_id="collective_bookable_offers",
        path="/offres/collectives",
        title="Offres collectives réservables",
        description=(
            "Liste des offres collectives réservables : suivre leur statut (publiée, préréservée par un enseignant, "
            "réservée, terminée, remboursée…), les modifier, les dupliquer ou les annuler."
        ),
        prerequisites="La structure doit être référencée sur ADAGE.",
        related_paths=(
            "/offre/:offerId/collectif/edition",
            "/offre/:offerId/collectif/recapitulatif",
            "/offre/:offerId/collectif/apercu",
            "/offre/:offerId/collectif/stocks/edition",
            "/offre/:offerId/collectif/informations-pratiques/edition",
            "/offre/:offerId/collectif/etablissement/edition",
        ),
    ),
    PortalPage(
        route_id="collective_template_offers",
        path="/offres/vitrines",
        title="Offres vitrines",
        description=(
            "Liste des offres collectives vitrines : offres sans date ni prix présentées aux enseignants sur ADAGE "
            "pour leur faire découvrir une activité et recevoir leurs demandes."
        ),
        prerequisites="La structure doit être référencée sur ADAGE.",
        related_paths=("/offre/:offerId/collectif/vitrine/apercu",),
    ),
    PortalPage(
        route_id="collective_venue_page",
        path="/partenaire/page-collective",
        title="Page dans ADAGE",
        description="Gérer la présentation de la structure visible par les enseignants sur la plateforme ADAGE.",
        prerequisites="La structure doit être référencée sur ADAGE.",
        related_paths=("/partenaire/page-collective/edition",),
    ),
    PortalPage(
        route_id="reimbursements_invoices",
        path="/administration/remboursements",
        title="Justificatifs de remboursement",
        description=(
            "Espace administration > Gestion financière : télécharger les justificatifs de remboursement "
            "et le détail des réservations remboursées."
        ),
        related_paths=("/administration/remboursements/justificatifs",),
    ),
    PortalPage(
        route_id="bank_information",
        path="/administration/remboursements/informations-bancaires",
        title="Informations bancaires",
        description=(
            "Espace administration > Gestion financière : ajouter ou remplacer un compte bancaire (démarche via "
            "demarche.numerique.gouv.fr) et choisir les structures remboursées sur chaque compte bancaire. "
            "Indispensable pour être remboursé des réservations validées."
        ),
    ),
    PortalPage(
        route_id="revenue",
        path="/administration/remboursements/revenus",
        title="Chiffre d'affaires",
        description="Espace administration > Gestion financière : consulter le chiffre d'affaires réalisé via le pass Culture.",
    ),
    PortalPage(
        route_id="activity_data_individual",
        path="/administration/donnees-activite/individuel",
        title="Données d'activité : individuel",
        description=(
            "Espace administration : télécharger (CSV ou Excel) les réservations individuelles de toute "
            "l'entité juridique, avec des filtres."
        ),
    ),
    PortalPage(
        route_id="activity_data_collective",
        path="/administration/donnees-activite/collectif",
        title="Données d'activité : collectif",
        description=(
            "Espace administration : télécharger les données des offres collectives réservables de toute "
            "l'entité juridique."
        ),
    ),
    PortalPage(
        route_id="collaborators",
        path="/administration/collaborateurs",
        title="Collaborateurs",
        description=(
            "Espace administration : inviter des collaborateurs par email à rejoindre l'entité juridique "
            "et voir la liste des membres et des invitations en attente."
        ),
    ),
    PortalPage(
        route_id="venue_general_information",
        path="/parametres/informations-generales",
        title="Paramètres : informations générales",
        description=(
            "Modifier les informations générales de la structure : nom affiché, adresse, activité principale, "
            "SIRET, coordonnées de contact."
        ),
        related_paths=("/parametres",),
    ),
    PortalPage(
        route_id="venue_notifications",
        path="/parametres/notifications",
        title="Paramètres : notifications",
        description="Choisir l'adresse email qui reçoit les notifications de réservation de la structure.",
    ),
    PortalPage(
        route_id="venue_synchronisations",
        path="/parametres/synchronisations",
        title="Paramètres : synchronisations",
        description=(
            "Connecter un logiciel de billetterie ou de gestion (cinéma, librairie, spectacle…) pour synchroniser "
            "automatiquement les offres et les stocks, mettre en pause ou supprimer une synchronisation."
        ),
    ),
    PortalPage(
        route_id="profile",
        path="/profil",
        title="Profil",
        description=(
            "Gérer son compte personnel : nom, prénom, email, téléphone, mot de passe, "
            "et demander la suppression de ses données personnelles."
        ),
    ),
    PortalPage(
        route_id="sitemap",
        path="/plan-du-site",
        title="Plan du site",
        description="Vue d'ensemble de toutes les pages de l'espace partenaire.",
    ),
)

PAGES_BY_ROUTE_ID: dict[str, PortalPage] = {page.route_id: page for page in PORTAL_PAGES}
ROUTE_IDS: tuple[str, ...] = tuple(page.route_id for page in PORTAL_PAGES)


def _path_to_regex(path: str) -> re.Pattern:
    segments = [r"[^/]+" if segment.startswith(":") else re.escape(segment) for segment in path.strip("/").split("/")]
    return re.compile("^/" + "/".join(segments) + "/?$")


# Most specific patterns first: more segments, then fewer `:param` segments
_PATH_PATTERNS: list[tuple[re.Pattern, str]] = [
    (_path_to_regex(path), page.route_id)
    for page in PORTAL_PAGES
    for path in sorted((page.path, *page.related_paths), key=lambda p: (-p.count("/"), p.count(":")))
]
_PATH_PATTERNS.sort(key=lambda item: (-item[0].pattern.count("/"), item[0].pattern.count("[^/]+")))


def find_route_id(path: str | None) -> str | None:
    """Return the `route_id` of the page matching `path`, or None if unknown."""
    if not path:
        return None
    path = path.split("?")[0].split("#")[0]
    for pattern, route_id in _PATH_PATTERNS:
        if pattern.match(path):
            return route_id
    return None


def render_for_prompt() -> str:
    lines = []
    for page in PORTAL_PAGES:
        lines.append(f"- route_id: {page.route_id}")
        lines.append(f"  titre: {page.title}")
        lines.append(f"  chemin: {page.path}")
        lines.append(f"  usage: {page.description}")
        if page.prerequisites:
            lines.append(f"  prérequis: {page.prerequisites}")
    return "\n".join(lines)
