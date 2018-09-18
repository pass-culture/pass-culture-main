### Contremarques [/booking/token]

Ceci décrit l'API utilisable par les partenaires techniques de Pass Culture qui souhaitent valider des contremarques.

**Statut actuel : ébauche, pour discussions**

##### Vérifier une contremarque [GET /bookings/token/\<token\>]

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

##### Valider une contremarque [POST /bookings/validate]
 Valide une contremarque (et la transaction associée).
 
 Un code contremarque est valide 1 semaine pour les offres physiques, 30 minutes pour les offres numériques.
 
 + Parameters
 
   + token (string) - le code de réservation
   + email (string) - correspond à l'email de la personne qui tente d'utiliser la contremarque pour obtenir une offre
   + offerId (optional, string) - identifiant de l'offre supposée correspondre à la réservation
 
 + Request (application/json)
 
     + Headers
        Authorization: Bearer xxxxx.yyyyy.zzzzz
 
     + Body
        { 
          "token": "AXB32J", 
          "email": "test@test.com",
          "offerId": "ABDE"
        }
 
 + Response 200 (application/json)
 
 + Response 400 (application/json)
 
     + Body
 
             [
               {
                  "token": "Code contremarque invalide"
               }
             ]
 
 + Response 400 (application/json)
 
     + Body
 
             [
               {
                  "global": "Contremarque déjà validée"
               }
             ]
 
 
 + Response 400 (application/json)
 
     + Body
 
             [
               {
                  "global": "Contremarque expirée"
               }
             ]
 
 
 + Response 400 (application/json)
 
     + Body
 
             [
               {
                  "global": "token et offerId ne correspondent pas"
               }
             ]
