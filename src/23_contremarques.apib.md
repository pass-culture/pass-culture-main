### Contremarques [/booking/token]

Ceci décrit l'API utilisable par les partenaires techniques de Pass Culture qui souhaitent valider des contremarques.

**Statut actuel : ébauche, pour discussions**

##### Vérifier une contremarque [GET /bookings/token/\<token\>]

Vérifie la validité d'une contremarque et récupère les informations de la transaction associée (uniquement si la contremarque est associée à une offre du partenaire identifié sur l'API).

+ Parameters

  + token (string) - le code de réservation
  + email (string) - correspond à l'email de la personne qui tente d'utiliser la contremarque pour obtenir une offre
  + offerId (optional, string) - identifiant de l'offre supposée correspondre à la réservation

+ Request (application/json)

    + Body
    
            [
              {
                 "token": "AXB32J", 
                 "email": "test@test.com",
                 "offerId": "ABDE"
              }
            ]

+ Response 204 (application/json) dans le cas où le partenaire n'est pas enregistré
            
+ Response 404 (application/json)

    + Body

            [
              {
                 "global": "Ce coupon n'a pas été trouvé"
              }
            ]

+ Response 400 (application/json)

    + Body

            [
              {
                 "email": "Vous devez préciser l\'email de l\'utilisateur quand vous n\'êtes pas connecté(e)"
              }
            ]
