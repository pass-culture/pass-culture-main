### Offers pour un PROFESSIONEL [/offers{?sellerId}]

+ Parameters

  + sellerId (required, string) - Identifiant du seller.

#### List toutes les *offers* [OPTIONS]

+ Request

    + Headers

            Authorization:Bearer bd2b9fa5-fbee-434f-9aaf-adc6701fd3db

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
