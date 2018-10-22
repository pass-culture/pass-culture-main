### Environnement d'intégration

L'équipe pass Culture met à disposition de ses partenaires techniques un environnement d'intégration pour leur permettre d'effectuer des tests et de valider le bon fonctionnement de leurs systèmes avec le pass Culture.

#### Adresses

- Portail professionnel : https://pro.passculture-integration.beta.gouv.fr
- Application web mobile "jeunes" : https://app.passculture-integration.beta.gouv.fr
- API : https://backend.passculture-integration.beta.gouv.fr

#### Fonctionnement

La création de comptes "Jeune" et "pro" sur cet environnement est libre. Les comptes "jeune" sont automatiquement crédités de 499€.

Attention : les sessions pro et jeune sont partagées. Il peut donc être utile d'utiliser le mode navigation privé pour l'un des deux pour avoir véritable un utilisateur "jeune" et un "pro". Les utilisateurs "pro" peuvent voir mais pas réserver les offres.

Lors de la création d'une offre coté "pro", pour la retrouver coté "jeune", il faut que l'offre ait :
- un prix (même égal à 0)
- des places disponibles
- une "accroche"
- une date limite de réservation dans le futur ou pas de date limite de réservation

### Utilisation des champs {token} et {offerId} pour les offres en lignes

Lors de la création d'une offre numérique (c'est à dire dont le contenu est accessible en ligne), il vous est demandé de remplir un champ URL. Ce champ correspond à l'URL sur laquelle vous souhaitez voir renvoyer un utilisateur ayant acheté votre offre sur l'application pass Culture.

Cette URL peut être personalisée en utilisant le modèle suivant : www.urldemonsite.fr/?email={email}&offerID={offerId}&token={token}

Ceci vous permet de faciliter l'inscription de l'utilisateur sur votre site en récuperant automatiquement :
+ l'adresse email de l'utilisateur ayant acheté votre offre
+ l'identifiant de l'offre (cet indentifiant correspond à l'URL de votre offre sur le portail professionnel, et une offre dont l'url est https://pro.passculture.beta.gouv.fr/offres/XX aura ainsi XX pour offerID)
+ la contremarque (token) générée par le pass Culture et vous permettant de valider la transaction
