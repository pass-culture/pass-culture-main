FORMAT: 1A
HOST: http://localhost:3001

# Pass Culture

This is the api of the Pass Culture project.


L'ontology se compose tout d'abord de deux types d'utilisateurs: des CLIENTS et des PROFESSIONNELS (de la culture). Chaque PROFESSIONNEL possède une entité *seller* et peuvent proposer des *offers* aux CLIENTS. Ceci consiste à proposer un *price* pour un certain groupe d'*événement* ou un *work*. Si le CLIENT accepte la transaction, ce dernier voit son carnet d'*orders* augmenter de ce dernier achat.

Pour connaître les préférences culturelles des CLIENTS, l'application pose des *questions* à ces derniers lors de son inscription.


### Events (object)

#### Properties
+ `endDate` (string, required)
+ `location` (string, required)
+ `offerId` (string, required)
+ `startDate` (string, required)


### Offers (object)

#### Properties
+ `comment` (string)
+ `editionDate` (string, required)
+ `sellerId` (string, required)
+ `thumbnailUrl` (string)
+ `workId` (string, required)


### Prices (object)

#### Properties
+ `condition` (string, required)
+ `eventId` (string, required)
+ `value` (string, required)


### Questions (object)

#### Properties
+ `choices` (array[string], required)


### Sellers (object)

#### Properties
+ `location` (object, required)
+ `thumbnailUrl` (string)


### UserQuestionJoins (object)

#### Properties
+ `choiceIndex` (number, required)
+ `questionId` (string, required)
+ `userId` (string, required)


### UserSellerJoins (object)

#### Properties
+ `sellerId` (string, required)
+ `userId` (string, required)


### Users (object)

#### Properties
+ `firstName` (string, required)
+ `lastName` (string, required)


### Works (object)

#### Properties
+ `composer` (string, required)
+ `date` (string, required)
+ `identifier` (string, required)
+ `name` (string, required)
+ `performer` (string, required)
+ `type` (string, required)


L'application côté CLIENT doit permettre à celui-ci d'obtenir les */offers* à sa proximité, ainsi que la possiblité de commander les */orders* correspondants.

L'application côté PROFESSIONNEL doit permettre à ces derniers d'ajouter des */offers* ainsi que les */works* qui leur sont asssociés.


### Offers

#### pour un PROFESSIONEL [/offers/pro/{?sellerId}]

+ Parameters

  + sellerId (required, string) - Identifiant du seller.

##### List toutes les *offers* [GET]

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


### Orders [/orders]

An order is a confirmation of a transaction made with the pass culture:
    - acceptedOffer is the product
    - confirmationNumber is the token that confirms the transaction
    - orderStatus says if the order is done or waiting
    - seller is the organization or the localBusinness selling the product.

#### List All Orders [GET]

+ Response 200 (application/json)

        [
            {
                "acceptedOffer": {
                    "authors": [
                        {
                            "id" : "58c2b1d7920ea806e862234e",
                            "name": "Albert Camus"
                        }
                    ],
                    "id" : "58c2b1d7920ea806e862230a",
                    "title": "La Chute",
                    "type": "book",
                    "published_at": "2015-08-05T09:40:51.620Z"
                },
                "confirmationNumber": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",
                "orderStatus": "done",
                "published_at": "2015-08-05T10:40:51.620Z",
                "seller":  {
                    "id" : "58c2b1d7920ea806e862230c",
                    "location": {
                            "address": "155 Rue Saint Honoré, 75001 Paris",
                            "geo": {
                                "latitude": 48.8619639,
                                "longitude": 2.3359426
                            }

                        },
                    "name": "Librairie Delamain",
                    "openingHours": "10AM-8PM"
                }
            }
        ]

#### Create New Order [POST]

When you are using the CLIENT part of the app, you may create your own order using this action.
    - customerId is the id of the client

+ Request (application/json)

        {
            "acceptedOfferId": "58c2b1d7920ea806e862230e",
            "customerId": "58c2b1d7920ea806e862335a",
            "sellerId": "58c2b1d7920ea806e862335b"
        }

+ Response 201 (application/json)

    + Headers

            Location: /orders/2

    + Body

            {
                "confirmationNumber": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9",
                "orderStatus": "waiting",
                "id" : "58c2b1d7920ea806e862231a",
                "published_at": "2015-08-05T10:40:51.620Z"
            }


### Works [/works]


