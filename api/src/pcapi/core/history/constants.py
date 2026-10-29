import enum


ACTION_HISTORY_ORDER_BY = "ActionHistory.actionDate.asc().nulls_first()"


class ActionType(enum.Enum):
    # Single comment from admin, on any resource, without status change:
    COMMENT = "COMMENT"
    # Update:
    INFO_MODIFIED = "INFO_MODIFIED"
    # Validation process for offerers:
    OFFERER_NEW = "OFFERER_NEW"
    OFFERER_PENDING = "OFFERER_PENDING"
    OFFERER_VALIDATED = "OFFERER_VALIDATED"
    OFFERER_REJECTED = "OFFERER_REJECTED"
    OFFERER_CLOSED = "OFFERER_CLOSED"
    OFFERER_SUSPENDED = "OFFERER_SUSPENDED"
    OFFERER_UNSUSPENDED = "OFFERER_UNSUSPENDED"
    OFFERER_ATTESTATION_CHECKED = "OFFERER_ATTESTATION_CHECKED"
    # Validation process for user-offerer relationships:
    USER_OFFERER_NEW = "USER_OFFERER_NEW"
    USER_OFFERER_PENDING = "USER_OFFERER_PENDING"
    USER_OFFERER_VALIDATED = "USER_OFFERER_VALIDATED"
    USER_OFFERER_REJECTED = "USER_OFFERER_REJECTED"
    USER_OFFERER_DELETED = "USER_OFFERER_DELETED"
    # User account status changes:
    USER_CREATED = "USER_CREATED"
    USER_SUSPENDED = "USER_SUSPENDED"
    USER_UNSUSPENDED = "USER_UNSUSPENDED"
    USER_PHONE_VALIDATED = "USER_PHONE_VALIDATED"
    USER_EMAIL_VALIDATED = "USER_EMAIL_VALIDATED"
    USER_ACCOUNT_UPDATE_INSTRUCTED = "USER_ACCOUNT_UPDATE_INSTRUCTED"
    USER_EXTRACT_DATA = "USER_EXTRACT_DATA"
    CONNECT_AS_USER = "CONNECT_AS_USER"
    USER_PASSWORD_INVALIDATED = "USER_PASSWORD_INVALIDATED"
    USER_DISCONNECTED = "USER_DISCONNECTED"
    # Fraud and compliance actions:
    BLACKLIST_DOMAIN_NAME = "BLACKLIST_DOMAIN_NAME"
    REMOVE_BLACKLISTED_DOMAIN_NAME = "REMOVE_BLACKLISTED_DOMAIN_NAME"
    FRAUD_INFO_MODIFIED = "FRAUD_INFO_MODIFIED"  # protected information

    # Finance incident events
    FINANCE_INCIDENT_CREATED = "FINANCE_INCIDENT_CREATED"
    FINANCE_INCIDENT_CANCELLED = "FINANCE_INCIDENT_CANCELLED"
    FINANCE_INCIDENT_VALIDATED = "FINANCE_INCIDENT_VALIDATED"
    FINANCE_INCIDENT_USER_RECREDIT = "FINANCE_INCIDENT_USER_RECREDIT"
    FINANCE_INCIDENT_WAIT_FOR_PAYMENT = "FINANCE_INCIDENT_WAIT_FOR_PAYMENT"
    FINANCE_INCIDENT_GENERATE_DEBIT_NOTE = "FINANCE_INCIDENT_GENERATE_DEBIT_NOTE"
    FINANCE_INCIDENT_CHOOSE_DEBIT_NOTE = "FINANCE_INCIDENT_CHOOSE_DEBIT_NOTE"

    # Non payment notices
    NON_PAYMENT_NOTICE_CREATED = "NON_PAYMENT_NOTICE_CREATED"

    # Actions related to a venue:
    VENUE_CREATED = "VENUE_CREATED"
    LINK_VENUE_BANK_ACCOUNT_DEPRECATED = "LINK_VENUE_BANK_ACCOUNT_DEPRECATED"
    LINK_VENUE_BANK_ACCOUNT_CREATED = "LINK_VENUE_BANK_ACCOUNT_CREATED"
    LINK_VENUE_PROVIDER_UPDATED = "LINK_VENUE_PROVIDER_UPDATED"
    LINK_VENUE_PROVIDER_DELETED = "LINK_VENUE_PROVIDER_DELETED"
    SYNC_VENUE_TO_PROVIDER = "SYNC_VENUE_TO_PROVIDER"
    VENUE_SOFT_DELETED = "VENUE_SOFT_DELETED"
    VENUE_REIMBURSEMENT_SUSPENDED = "VENUE_REIMBURSEMENT_SUSPENDED"
    VENUE_CLOSED = "VENUE_CLOSED"
    VENUE_REOPENED = "VENUE_REOPENED"

    # Permissions role changes:
    ROLE_PERMISSIONS_CHANGED = "ROLE_PERMISSIONS_CHANGED"
    # RGPD scripts
    USER_ANONYMIZED = "USER_ANONYMIZED"
    # Offer validation rule changes:
    RULE_CREATED = "RULE_CREATED"
    RULE_DELETED = "RULE_DELETED"
    RULE_MODIFIED = "RULE_MODIFIED"
    # Pivot changes
    PIVOT_DELETED = "PIVOT_DELETED"
    PIVOT_CREATED = "PIVOT_CREATED"
    # Chronicles
    CHRONICLE_PUBLISHED = "CHRONICLE_PUBLISHED"
    CHRONICLE_UNPUBLISHED = "CHRONICLE_UNPUBLISHED"
    # User profile refresh campaigns
    USER_PROFILE_REFRESH_CAMPAIGN_CREATED = "USER_PROFILE_REFRESH_CAMPAIGN_CREATED"
    USER_PROFILE_REFRESH_CAMPAIGN_UPDATED = "USER_PROFILE_REFRESH_CAMPAIGN_UPDATED"

    # Legacy, used during regularization. Some venues have this Action Type in their history.
    VENUE_REGULARIZATION = "VENUE_REGULARIZATION"


ACTION_TYPE_TO_STRING = {
    ActionType.COMMENT: "Commentaire interne",
    # Update:
    ActionType.INFO_MODIFIED: "Modification des informations",
    # Validation process for offerers:
    ActionType.OFFERER_NEW: "Nouvelle entité juridique",
    ActionType.OFFERER_PENDING: "Entité juridique mise en attente",
    ActionType.OFFERER_VALIDATED: "Entité juridique validée",
    ActionType.OFFERER_REJECTED: "Entité juridique rejetée",
    ActionType.OFFERER_CLOSED: "Entité juridique fermée",
    ActionType.OFFERER_SUSPENDED: "Entité juridique désactivée",
    ActionType.OFFERER_UNSUSPENDED: "Entité juridique réactivée",
    ActionType.OFFERER_ATTESTATION_CHECKED: "Attestation consultée",
    # Validation process for user-offerer relationships:
    ActionType.USER_OFFERER_NEW: "Nouveau rattachement",
    ActionType.USER_OFFERER_PENDING: "Rattachement mis en attente",
    ActionType.USER_OFFERER_VALIDATED: "Rattachement validé",
    ActionType.USER_OFFERER_REJECTED: "Rattachement rejeté",
    ActionType.USER_OFFERER_DELETED: "Rattachement supprimé, sans mail envoyé",
    # User account status changes:
    ActionType.USER_CREATED: "Création du compte",
    ActionType.USER_SUSPENDED: "Compte suspendu",
    ActionType.USER_UNSUSPENDED: "Compte réactivé",
    ActionType.USER_PHONE_VALIDATED: "Validation manuelle du numéro de téléphone",
    ActionType.USER_EMAIL_VALIDATED: "Validation manuelle de l'email",
    ActionType.USER_ACCOUNT_UPDATE_INSTRUCTED: "Instruction d'une demande de modifications",
    ActionType.USER_EXTRACT_DATA: "Génération d'un extrait des données du compte",
    ActionType.CONNECT_AS_USER: "Connexion d'un admin",
    ActionType.USER_DISCONNECTED: "Déconnexion de l'utilisateur",
    ActionType.USER_PASSWORD_INVALIDATED: "Invalidation du mot de passe de l'utilisateur",
    # Fraud and compliance actions:
    ActionType.BLACKLIST_DOMAIN_NAME: "Blacklist d'un nom de domaine",
    ActionType.REMOVE_BLACKLISTED_DOMAIN_NAME: "Suppression d'un nom de domaine banni",
    ActionType.FRAUD_INFO_MODIFIED: "Fraude et Conformité",  # protected information
    # Finance incident events
    ActionType.FINANCE_INCIDENT_CREATED: "Création de l'incident",
    ActionType.FINANCE_INCIDENT_CANCELLED: "Annulation de l'incident",
    ActionType.FINANCE_INCIDENT_VALIDATED: "Validation de l'incident",
    ActionType.FINANCE_INCIDENT_USER_RECREDIT: "Compte re-crédité suite à un incident",
    ActionType.FINANCE_INCIDENT_WAIT_FOR_PAYMENT: "Attente de la prochaine échéance de remboursement",
    ActionType.FINANCE_INCIDENT_GENERATE_DEBIT_NOTE: "Une note de débit va être générée",
    ActionType.FINANCE_INCIDENT_CHOOSE_DEBIT_NOTE: "Choix note de débit",
    # Actions related to a venue:
    ActionType.VENUE_CREATED: "Partenaire culturel créé",
    ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED: "Partenaire culturel dissocié d'un compte bancaire",
    ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED: "Partenaire culturel associé à un compte bancaire",
    ActionType.LINK_VENUE_PROVIDER_UPDATED: "Lien avec le partenaire technique modifié",
    ActionType.LINK_VENUE_PROVIDER_DELETED: "Suppression du lien avec le partenaire technique",
    ActionType.SYNC_VENUE_TO_PROVIDER: "Synchronisation du partenaire culturel avec un partenaire technique",
    ActionType.VENUE_CLOSED: "Fermeture du partenaire culturel",
    ActionType.VENUE_REOPENED: "Réouverture du partenaire culturel",
    ActionType.VENUE_REGULARIZATION: "Régularisation des partenaires culturels",
    ActionType.VENUE_SOFT_DELETED: "Suppression réversible",
    ActionType.VENUE_REIMBURSEMENT_SUSPENDED: "Blocage des remboursements",
    # Actions related to an offerer and/or a venue:
    ActionType.NON_PAYMENT_NOTICE_CREATED: "Saisie d'un avis d'impayé",
    # Permissions role changes:
    ActionType.ROLE_PERMISSIONS_CHANGED: "Modification des permissions du rôle",
    # RGPD scripts
    ActionType.USER_ANONYMIZED: "Le compte a été anonymisé conformément au RGPD",
    # Offer validation rule changes:
    ActionType.RULE_CREATED: "Création d'une règle de conformité",
    ActionType.RULE_DELETED: "Suppression d'une règle de conformité",
    ActionType.RULE_MODIFIED: "Modification d'une règle de conformité",
    # Pivot changes
    ActionType.PIVOT_DELETED: "Suppression d'un pivot",
    ActionType.PIVOT_CREATED: "Création d'un pivot",
    # Chronicles
    ActionType.CHRONICLE_PUBLISHED: "Publication d'une chronique",
    ActionType.CHRONICLE_UNPUBLISHED: "Dépublication d'une chronique",
    # User profile refresh campaign
    ActionType.USER_PROFILE_REFRESH_CAMPAIGN_CREATED: "Création de campagne de mise à jour de données",
    ActionType.USER_PROFILE_REFRESH_CAMPAIGN_UPDATED: "Modification de campagne de mise à jour de données",
}
