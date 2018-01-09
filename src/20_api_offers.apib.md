### Offres [/offers{?sellerId}]

+ Parameters

  + sellerId (optional, string) - Identifiant du "seller" (fournisseur de l'offre)
  + around: 37.423021,-122.083739 (optional, string) - Coordonnées de l'endroit autour duquel afficher les offres
  + radius: 2 (optional, integer) - Rayon autour de l'endroit dans lequel afficher les offres

#### Lister des offres [GET]

+ Request

+ Response 200 (application/json)

    + Body

            [
               {
                 "category": "theater",
                 "events": [
                    {
                      "endDate": "2017-05-10T19:00:00+00:00",
                      "id" : "58c2b1d7920ea816e861233e",
                      "location": "1 Place Colette, 75001 Paris",
                      "startDate": "2017-05-10T22:00:00+00:00"
                    }
                  ],
                  "id" : "58c2b1d7920ea806e862230e",
                  "name": "Le Misanthrope",
                  "thumbnailUrl": "https://upload.wikimedia.org/wikipedia/commons/0/08/LeMisanthrope.jpg"
                }
            ]

+ Response 400 (application/json)

    + Body

            [
               {
                 "text": "Wrong"
                }
            ]
