### Fournisseurs

#### Les Stocks [/stocks/{siret}]

+ Parameters

  + siret (optional, number) - Identifiant du "siret"

###### Lister les stocks disponible pour un établissement [GET]

+ Request

+ Response 200 (application/json)

    + Body

            [
              {
                  "ref": "978-2-1234-5680-3",
                  "quantity": 27
              },
              {
                  "ref": "978-2-1234-5681-3",
                  "quantity": 3
              }
            ]

+ Response 400 (application/json)

    + Body

            [
              {
                 "text": "Siret invalide"
              }
            ]
