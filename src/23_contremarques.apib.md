### Contremarques [/booking/token]

**Statut actuel : protype, pour implémentations pilotes**

#### Principe de l'API contremarque

Ceci décrit l'API utilisable par les partenaires techniques de Pass Culture qui souhaitent valider des contremarques.

Le parcours utilisateur pour souscrire à une offre en passant par le pass Culture est le suivant :
+ L'utilisateur réserve l'offre sur l'application pass Culture. 
+ Cette réservation déclenche les actions suivantes :
  + Le compte pass Culture de l'utilisateur est décredité du montant de votre offre
  + Il reçoit en contrepartie un code contremarque
  + Dans le cas d'une offre en ligne, l'utilisateur reçoit par ailleur un lien pour accéder à l'offre
+ L’utilisateur se rend ensuite sur ce lien, ce qui permet à l'acteur ayant proposé l'offre de prendre la main sur la suite de la gestion de la relation. 

Afin de vérifier que l’utilisateur vient bien du pass Culture et a bien reservé l'offre en question sur l'application, il suffit alors de lui demander d’indiquer le code contremarque. L'API décrite ci-dessous permet de vérifier que ce code contremarque est bien valable et correspond bien à l'offre. 

#### Utilisation de l'API contremarque

Pour l'environnement de production, les API sont disponibles à l'URL suivante : https://backend.passculture.beta.gouv.fr

L'utilisation des deux API de vérification de validité et de validation d'une contremarque utilisent trois paramètres :
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
 
