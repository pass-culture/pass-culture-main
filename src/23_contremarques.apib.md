### Contremarques [/booking/]

Ceci décrit l'API utilisable par les partenaires techniques de Pass Culture qui souhaitent valider des contremarques.

Les partenaires s'identifient auprès de l'API Pass Culture à l'aide d'un jeton disponible dans la section "structure" du portail pro.

**Statut actuel : ébauche, pour discussions**

##### Vérifier une contremarque [GET /bookings/<token>]

Vérifie la validité d'une contremarque et récupère les informations de la transaction associée (uniquement si la contremarque est associée à une offre du partenaire identifié sur l'API).

+ Parameters

  + token (string) - le code de réservation
  + email (optional, string) - correspond à l'email de la personne qui tente d'utiliser la contremarque pour obtenir une offre
  + offerId (optional, string) - identifiant de l'offre supposée correspondre à la réservation

+ Request (application/json)

    + Headers
       Authorization: Bearer xxxxx.yyyyy.zzzzz

    + Body
    
            [
              {
                 "token": "AXB32J", 
                 "email": "test@test.com",
                 "offerId": "ABDE"
              }
            ]

+ Response 200 (application/json)

    + Body

            [
              {
                 "global": "OK",
                 "email": "test@test.com",
                 "userId": "Rosa",
                 "offerId": "ABDE",
                 "bookingId": "XYZ",
              }
            ]
            
+ Response 400 (application/json)

    + Body

            [
              {
                 "global": "Code contremarque invalide"
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
                 "global": "Vous ne disposez pas des droits pour accéder à cette contremarque"
              }
            ]

##### Valider une contremarque [POST /bookings/validate]

Valide une contremarque (et la transaction associée).

Un code contremarque est valide 1 semaine pour les offres physiques, 30 minutes pour les offres numériques.

+ Parameters

  + email (optional, string) - obligatoire pour les offres numériques, correspond à l'email de la personne qui tente d'utiliser la contremarque pour obtenir une offre
  + token (string) - le code de réservation
  + offerId (optional, string) - identifiant de l'offre supposée correspondre à la réservation. Obligatoire pour les offres numériques.

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
