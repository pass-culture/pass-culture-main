### Fournisseurs

Ceci décrit l'API à implémenter par les partenaires techniques de Pass Culture qui souhaitent fournir des stocks.

Pass Culture s'identifie auprès des partenaires techniques via un certificat client SSL. La clé publique est publiée sur le site Pass Culture, et les partenaires sont prévenus à l'avance en cas de changement de clé via notre liste de diffusion email "partenaires techniques".

**Statut actuel : protype, pour implémentations pilotes**

#### Les Stocks [/stocks/{siret}]

Cette API est apellée immédiatement lorsqu'un offreur culturel vous choisit comme fournisseur dans le portail, puis une fois par nuit et par offreur vous ayant choisi par la suite.

Règles de mise à jour des données dans Pass Culture:
- Si la requête reçoit une réponse, on écrase toutes les données précédentes
- Si pas de retour on essaye une seconde fois, puis une alerte vous est envoyé par mail
- Si pas de retour après 2 jours, on efface toutes les données (tous les stocks à 0), mais les appels continuent.


+ Parameters

  + siret (optional, string) - Identifiant "siret" du commerce.
  + after (optional, string) - pagination : EAN13 de la dernière entrée traitée (le dernier de la page précédente)
  + limit (optional, integer) - pagination : nombre maximum d'entrées à renvoyer pour cette requête
  + modifiedSince (optional, string) - date au format 2012-04-23T18:25:43.511Z. L'API ne renvoie que les stocks modifiés depuis cette date

###### Lister les stocks disponible pour un établissement [GET /stocks/12345678901234?after=1978212345681&limit=2]

Les références renvoyées sont les EAN13 du code barre du produit. 

L'ordre est au choix du fournisseur mais ne doit pas varier entre deux requetes.

"total" représente le nombre total d'entrées (nombre de références donc, ou presque, cf. le sujet du prix ci-dessous) disponibles.
"limit" indique le nombre d'entrées maximum retournées pour une requete. Il est inférieur ou égal au paramètre limit envoyé dans la requete (inférieur si le serveur souhaite limiter, égal sinon)
"offset" représente le nombre d'entrées précedent celles qui sont présentées

Dans une entrée,
- "available" est le stock disponible pour la référence "ref".
- "price" est le prix auquel on souhaite vendre ce stock. On peut avoir deux entrées pour une même référence si on souhaite vendre à deux prix différents. Par exemple pour faire un prix d'appel : 10€ pour les 10 premiers, 12€ ensuite. Le prix est optionnel pour les livres (prix unique).
- "validUntil" (optionnel) est la date au format 2012-04-23T18:25:43.511Z de fin de validité de l'offre (prix). Passé cette date, on considère que le stock est à zéro pour cette entrée.

+ Request

+ Response 200 (application/json)

    + Body

            { 
              "total": 23,
              "limit": 20,
              "offset": 20,
              "stocks":
                [
                  {
                    "ref": "1978212345680",
                    "available": 27,
                    "price": 22.99,
                    "validUntil": "2018-08-23T18:25:43.511Z"
                },
                {
                  "ref": "1978212345682",
                  "available": 3
                }
              ]
            }

+ Response 400 (application/json)

    + Body

            {
                "errors": { "siret": [ "Siret invalide" ], "after" : [ "Entrée non trouvée" ] }
            }


+ Response 404 (application/json)

    + Body

            {
                "errors": { "siret": [ "Siret inexistant" ] }
            }
