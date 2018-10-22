### Contremarques [/booking/token]

Ceci décrit l'API utilisable par les partenaires techniques de Pass Culture qui souhaitent valider des contremarques.

**Statut actuel : protype, pour implémentations pilotes**

#### Fonctionnement des API

Pour l'environnement de production, les API sont disponibles à l'URL suivante : https://backend.passculture.beta.gouv.fr

L'utilisation des deux API de vérification de validité et de validation d'une contremarque utilisent les trois paramètre suivants :
  + token : ce champ désigne la contremarque qui permet aux acteurs de valider que l’utilisateur qui se présente devant lui dispose bien d'un compte pass Culture et a bien reservé l'offre correspondante sur l'application mobile. Ce code est généré en temps réel pour chaque réservation d'un utilisateur sur l'application et est transmis à cette occasion à l’utilisateur.
  + email (string) : ce champ désigne l'adresse de messagerie électronique de l'utilisateur.
  + offerId (optional, string) : ce champ désigne l'identifiant unique d'une offre sur notre plateforme. Vous le trouverez sur l'URL de votre offre sur le portail professionnel (une offre dont l'url est https://pro.passculture.beta.gouv.fr/offres/XX aura ainsi XX pour offerID)

#### Vérifier une contremarque [GET /bookings/token/\<token\>?email=\<email\>&offer_id=\<offer_id\>]

+ Parameters

  + token (string) - le code de réservation
  + email (string) - correspond à l'email de la personne qui tente d'utiliser la contremarque pour obtenir une offre
  + offerId (optional, string) - identifiant de l'offre supposée correspondre à la réservation

+ Request (application/json)

    + Body {}

+ Response 204 (application/json) dans le cas où le partenaire n'est pas enregistré
            
+ Response 404 (application/json)

    + Body

          {
             "global": [ "Ce coupon n'a pas été trouvé" ]
          }

+ Response 400 (application/json)

    + Body
    
          {
             "email": [ "Vous devez préciser l\'email de l\'utilisateur quand vous n\'êtes pas connecté(e)" ]
          }

#### Valider une contremarque [PATCH /bookings/token/<token>?email=\<email\>&offer_id=\<offer_id\>]

Valide une contremarque (et la transaction associée). Le partenaire doit renseigner les paramètres <email> et <offer_id>.

+ Parameters
  + token (string) - le code de réservation
  + email (string) - correspond à l'email de la personne qui tente d'utiliser la contremarque pour obtenir une offre
  + offer_id (string) - identifiant de l'offre supposée correspondre à la réservation

+ Request (application/json)

    + Body {}

+ Response 204 (application/json)

+ Response 400 (application/json)

    + Body
    
          {
             "global": [ "L'adresse email qui a servie à la réservation est obligatoire dans l'URL [?email=<email>]" ]
          }

+ Response 400 (application/json)

    + Body

          {
             "global": [ "L'id de l'offre réservée est obligatoire dans l'URL [?offer_id=<id>]" ]
          }
    
+ Response 404 (application/json)

    + Body

          {
             "global": [ "Cette contremarque n'a pas été trouvée" ]
          }

+ Response 410 (application/json)

    + Body

          {
             "booking": [ "Cette réservation a été annulée" ]
          }


+ Response 410 (application/json)

    + Body

          {
             "booking": [ "Cette réservation a déjà été validée" ]
          }
 
