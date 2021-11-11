# API Fournisseurs

Ces API peuvent être implémentées par les partenaires techniques du pass Culture qui souhaitent fournir des informations relatives à des évolutions de stocks ou places pour des objets ou événements de manière automatisée. Les différentes sections de l'API sont indépendantes et ne sont donc pas nécessairement toutes à implémenter.

Ces API ont vocation à être appelées immédiatement lorsqu'un acteur culturel choisit un fournisseur dans le portail, puis une fois par nuit et par acteur par la suite.

Seule l'API pour les stocks de livre est à ce jour accessible.

Avant de développer un interfaçage, merci de contacter contact.api@passculture.app afin d’être référencé comme fournisseur pass Culture.

## Règles API Stocks (valable pour les livres)

Règles de mise à jour des données dans le pass Culture
- si la requête reçoit une réponse, toutes les données précédentes sont effacées
- si la requête ne reçoit pas de réponse après deux appels, une alerte vous est envoyée par mail
- si la requête ne reçoit pas de réponse après 2 jours, les données sont effacées (les stocks sont remis à 0), mais les appels continuent.

### Paramètres d’appel
 
- “SIRET” (string) : identifiant SIRET du lieu dans lequel sont localisées les propositions 
- “modifiedSince” (string) - date au format aaaa-mm-ddThh:mm:ss.mmmZ. L'API ne renvoie que les événements ou objets modifiés depuis cette date. Techniquement, ce champ n'est pas obligatoire, mais pour des raisons de performances nous invitons fortement à son utilisation.
- “after” (optional, string) - pagination : référence (ex : EAN13) de la dernière entrée traitée (le dernier de la page précédente)
- “limit” (optional, integer) - pagination : nombre maximum d'entrées (nombre de couples (référence; prix)) à renvoyer pour cette requête. Nous fixons généralement une valeur arbitraire lors de l'appel à 1000 résultats. Tel que notre système fonctionne, nous effectuons des requêtes paginées jusqu'à recevoir aucun résultat.

Par exemple, pour lister les stocks disponible pour un établissement : GET /stocks/12345678901234?after=1978212345681&limit=2

Note: Lors de l'établissement de la liaison entre un établissement et un fournisseur, nous effectuons un premier appel avec pour seul paramètre :
- “SIRET” (string) : identifiant SIRET du lieu dans lequel sont localisées les propositions 

Si l'API renvoie un code 200, cela nous permet de nous assurer que le lieu est bien reconnu par le fournisseur. 

### Paramètres de réponse

L'ordre des paramètres est au choix du fournisseur mais ne doit pas varier entre deux requêtes.

Note : les paramètres sont attendus en minuscules.

Les paramètres "total" et "offset" sont des informations retournées en sortie par l'API. Ils sont présents à titre informatifs et pas utilisés lors du traitement des données :
- "total" (optional, integer) : nombre total d'entrées (nombre de couples (référence; prix)) dans la requête 
- "offset" (optional, integer) : nombre d'entrées précédent celles qui sont présentées

Un paramètre "stocks" doit ainsi comporter : 
- "ref" : EAN13 (correspondant à l’ISBN pour les livres)
- "available" : stock disponible
- "price" : prix auquel sont vendus l’ensemble des éléments du stock. Il est ainsi possible d’avoir plusieurs entrées pour une même référence, si plusieurs tarifs sont appliqués (par exemple, dans le cas d’un prix d'appel, 10€ pour les 10 premiers, 12€ ensuite). 
Dans le cas des livres, si aucun prix n’est rentré, le prix unique est automatiquement récupéré.
- "validUntil" (optionnel) : date au format aaa-mm-ddThh:mm:ss.mmmZ de fin de validité du stock en question. Passé cette date, on considère le stock est remis à zéro pour cette entrée. Si aucune date n’est indiquée, la proposition est considérée comme étant à durée illimitée.


### Request

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

+ Response 400 (application/json) : vous pouvez retourner cette erreur lorsque les paramètres d'appels sont erronés ou manquants (Par exemple, mauvais format de date)

    + Body

            {
                "errors": { "siret": [ "Siret invalide" ], "after" : [ "Entrée non trouvée" ] }
            }


+ Response 404 (application/json) : ce code doit être retourné lorsque l'identifiant du lieu est inconnu dans votre système

    + Body

            {
                "errors": { "siret": [ "Siret inexistant" ] }
            }

