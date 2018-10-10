### Contremarques [/booking/token]

Ceci décrit l'API utilisable par les partenaires techniques de Pass Culture qui souhaitent valider des contremarques.

**Statut actuel : protype, pour implémentations pilotes**

##### Vérifier une contremarque [GET /bookings/token/\<token\>?email=\<email\>&offer_id=\<offer_id\>]

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

##### Valider une contremarque [PATCH /bookings/token/<token>?email=\<email\>&offer_id=\<offer_id\>]

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
 
