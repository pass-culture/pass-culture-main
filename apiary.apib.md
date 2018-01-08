FORMAT: 1A
HOST: http://localhost:3001

# Pass Culture

This is the api of the Pass Culture project.


## Ontology

L'ontology se compose tout d'abord de deux types d'utilisateurs: des CLIENTS et des PROFESSIONNELS (de la culture). Chaque PROFESSIONNEL possède une entité *seller* et peuvent proposer des *offers* aux CLIENTS. Ceci consiste à proposer un *price* pour un certain groupe d'*événement* ou un *work*. Si le CLIENT accepte la transaction, ce dernier voit son carnet d'*orders* augmenter de ce dernier achat.

Pour connaître les préférences culturelles des CLIENTS, l'application pose des *questions* à ces derniers lors de son inscription.

## Data Structures


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
+ `id` (string, required)
+ `name` (string, required)
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
+ `category` (string, required)
+ `composer` (string, required)
+ `date` (string, required)
+ `identifier` (string, required)
+ `name` (string, required)
+ `performer` (string, required)
+ `thumbnailUrl` (string)


## API

L'application côté CLIENT */client* doit permettre aux utilisateurs d'obtenir les *offers* à sa proximité, ainsi que la possiblité de commander les *orders* correspondants.

L'application côté PROFESSIONNEL */pro* doit permettre à des utilisateurs *sellers* d'ajouter des */offers* ainsi que les */works* qui leur sont asssociés.


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


