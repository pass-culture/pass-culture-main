from pcapi.core.history import models as history_models


ACTION_HISTORY_ORDER_BY = "ActionHistory.actionDate.asc().nulls_first()"

ACTION_TYPE_TO_STRING = {
    history_models.ActionType.COMMENT: "Commentaire interne",
    # Update:
    history_models.ActionType.INFO_MODIFIED: "Modification des informations",
    # Validation process for offerers:
    history_models.ActionType.OFFERER_NEW: "Nouvelle entité juridique",
    history_models.ActionType.OFFERER_PENDING: "Entité juridique mise en attente",
    history_models.ActionType.OFFERER_VALIDATED: "Entité juridique validée",
    history_models.ActionType.OFFERER_REJECTED: "Entité juridique rejetée",
    history_models.ActionType.OFFERER_CLOSED: "Entité juridique fermée",
    history_models.ActionType.OFFERER_SUSPENDED: "Entité juridique désactivée",
    history_models.ActionType.OFFERER_UNSUSPENDED: "Entité juridique réactivée",
    history_models.ActionType.OFFERER_ATTESTATION_CHECKED: "Attestation consultée",
    # Validation process for user-offerer relationships:
    history_models.ActionType.USER_OFFERER_NEW: "Nouveau rattachement",
    history_models.ActionType.USER_OFFERER_PENDING: "Rattachement mis en attente",
    history_models.ActionType.USER_OFFERER_VALIDATED: "Rattachement validé",
    history_models.ActionType.USER_OFFERER_REJECTED: "Rattachement rejeté",
    history_models.ActionType.USER_OFFERER_DELETED: "Rattachement supprimé, sans mail envoyé",
    # User account status changes:
    history_models.ActionType.USER_CREATED: "Création du compte",
    history_models.ActionType.USER_SUSPENDED: "Compte suspendu",
    history_models.ActionType.USER_UNSUSPENDED: "Compte réactivé",
    history_models.ActionType.USER_PHONE_VALIDATED: "Validation manuelle du numéro de téléphone",
    history_models.ActionType.USER_EMAIL_VALIDATED: "Validation manuelle de l'email",
    history_models.ActionType.USER_ACCOUNT_UPDATE_INSTRUCTED: "Instruction d'une demande de modifications",
    history_models.ActionType.USER_EXTRACT_DATA: "Génération d'un extrait des données du compte",
    history_models.ActionType.CONNECT_AS_USER: "Connexion d'un admin",
    history_models.ActionType.USER_DISCONNECTED: "Déconnexion de l'utilisateur",
    history_models.ActionType.USER_PASSWORD_INVALIDATED: "Invalidation du mot de passe de l'utilisateur",
    # Fraud and compliance actions:
    history_models.ActionType.BLACKLIST_DOMAIN_NAME: "Blacklist d'un nom de domaine",
    history_models.ActionType.REMOVE_BLACKLISTED_DOMAIN_NAME: "Suppression d'un nom de domaine banni",
    history_models.ActionType.FRAUD_INFO_MODIFIED: "Fraude et Conformité",  # protected information
    # Finance incident events
    history_models.ActionType.FINANCE_INCIDENT_CREATED: "Création de l'incident",
    history_models.ActionType.FINANCE_INCIDENT_CANCELLED: "Annulation de l'incident",
    history_models.ActionType.FINANCE_INCIDENT_VALIDATED: "Validation de l'incident",
    history_models.ActionType.FINANCE_INCIDENT_USER_RECREDIT: "Compte re-crédité suite à un incident",
    history_models.ActionType.FINANCE_INCIDENT_WAIT_FOR_PAYMENT: "Attente de la prochaine échéance de remboursement",
    history_models.ActionType.FINANCE_INCIDENT_GENERATE_DEBIT_NOTE: "Une note de débit va être générée",
    history_models.ActionType.FINANCE_INCIDENT_CHOOSE_DEBIT_NOTE: "Choix note de débit",
    # Actions related to a venue:
    history_models.ActionType.VENUE_CREATED: "Partenaire culturel créé",
    history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED: "Partenaire culturel dissocié d'un compte bancaire",
    history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED: "Partenaire culturel associé à un compte bancaire",
    history_models.ActionType.LINK_VENUE_PROVIDER_UPDATED: "Lien avec le partenaire technique modifié",
    history_models.ActionType.LINK_VENUE_PROVIDER_DELETED: "Suppression du lien avec le partenaire technique",
    history_models.ActionType.SYNC_VENUE_TO_PROVIDER: "Synchronisation du partenaire culturel avec un partenaire technique",
    history_models.ActionType.VENUE_CLOSED: "Fermeture du partenaire culturel",
    history_models.ActionType.VENUE_REOPENED: "Réouverture du partenaire culturel",
    history_models.ActionType.VENUE_REGULARIZATION: "Régularisation des partenaires culturels",
    history_models.ActionType.VENUE_SOFT_DELETED: "Suppression réversible",
    history_models.ActionType.VENUE_REIMBURSEMENT_SUSPENDED: "Blocage des remboursements",
    # Actions related to an offerer and/or a venue:
    history_models.ActionType.NON_PAYMENT_NOTICE_CREATED: "Saisie d'un avis d'impayé",
    # Permissions role changes:
    history_models.ActionType.ROLE_PERMISSIONS_CHANGED: "Modification des permissions du rôle",
    # RGPD scripts
    history_models.ActionType.USER_ANONYMIZED: "Le compte a été anonymisé conformément au RGPD",
    # Offer validation rule changes:
    history_models.ActionType.RULE_CREATED: "Création d'une règle de conformité",
    history_models.ActionType.RULE_DELETED: "Suppression d'une règle de conformité",
    history_models.ActionType.RULE_MODIFIED: "Modification d'une règle de conformité",
    # Pivot changes
    history_models.ActionType.PIVOT_DELETED: "Suppression d'un pivot",
    history_models.ActionType.PIVOT_CREATED: "Création d'un pivot",
    # Chronicles
    history_models.ActionType.CHRONICLE_PUBLISHED: "Publication d'une chronique",
    history_models.ActionType.CHRONICLE_UNPUBLISHED: "Dépublication d'une chronique",
    # User profile refresh campaign
    history_models.ActionType.USER_PROFILE_REFRESH_CAMPAIGN_CREATED: "Création de campagne de mise à jour de données",
    history_models.ActionType.USER_PROFILE_REFRESH_CAMPAIGN_UPDATED: "Modification de campagne de mise à jour de données",
}
