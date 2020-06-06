### API Fournisseurs

Ces API peuvent être implémentées par les partenaires techniques de Pass Culture qui souhaitent fournir des informations relatives à des évolutions de stocks ou places pour des objets ou événements de manière automatisée. Les différentes sections de l'API sont indépendantes et ne sont donc pas nécessairement toutes à implémenter.

Ces API ont vocation à être appelées immédiatement lorsqu'un acteur culturel choisit un fournisseur dans le portail, puis une fois par nuit et par acteur par la suite.

Avant de développer un interfaçage, merci de contacter produit@passculture.app afin d’être référencé comme fournisseur pass Culture.

###### Règles générales 

Règles de mise à jour des données dans le pass Culture
- si la requête reçoit une réponse, toutes les données précédentes sont effacées
- si la requête ne reçoit pas de réponse après deux appels, une alerte vous est envoyée par mail

###### Stocks disponibles pour des objets (livres, CD...) 

### Règle particulière d'appel

- si la requête ne reçoit pas de réponse après 2 jours, les données sont effacées (les stocks sont remis à 0), mais les appels continuent.

### Paramètres d’appel
 
- “SIRET” (string) : identifiant SIRET du lieu dans lequel sont localisées les propositions 
- “modifiedSince” (string) - date au format aaa-mm-ddThh:mm:ss.mmmZ. L'API ne renvoie que les événements ou objets modifiés depuis cette date
- “after” (optional, string) - pagination : référence (ex : EAN13) de la dernière entrée traitée (le dernier de la page précédente)
- “limit” (optional, integer) - pagination : nombre maximum d'entrées (nombre de couples (référence; prix)) à renvoyer pour cette requête
- "total" (optional, integer) : nombre total d'entrées (nombre de couples (référence; prix)) dans la requête 
- "offset" (optional, integer) : nombre d'entrées précédent celles qui sont présentées

Par exemple, pour lister les stocks disponible pour un établissement : GET /stocks/12345678901234?after=1978212345681&limit=2

### Paramètres de réponse

L'ordre des paramètres est au choix du fournisseur mais ne doit pas varier entre deux requêtes.

Un paramètre "stocks" dit ainsi comporter : 
- "ref" : EAN13 (correspondant à l’ISBN pour les livres, notamment)
- "available" : stock disponible
- "price" : prix auquel sont vendus l’ensemble des éléments du stock. Il est ainsi possible d’avoir plusieurs entrées pour une même référence, si plusieurs tarifs sont appliqués (par exemple, dans le cas d’un prix d'appel, 10€ pour les 10 premiers, 12€ ensuite). 
Dans le cas des livres, si aucun prix n’est rentré, le prix unique est alors considéré.
- "validUntil" (optionnel) : date au format aaa-mm-ddThh:mm:ss.mmmZ de fin de validité du stock en question. Passé cette date, on considère le stock est remis à zéro pour cette entrée. Si aucune date n’est indiquée, la proposition est considérée comme étant à durée illimitée.


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



#### Les évènements [/events/{siret}]

**Statut actuel : brouillon**

### Règle particulière d'appel
- Un évenement ou une occurence (date) future qui figurait dans un appel précédent mais ne figure plus pour ce lieu est considéré comme étant à ne plus afficher dans Pass Culture. S'il y a déjà des réservations dans Pass Culture pour cet évennement ou cette date, les réservations seront anullées.

+ Parameters

  + siret (optional, string) - Identifiant "siret" de l'acteur
  + after (optional, string) - pagination : référence de la dernière entrée (évenement) traitée (le dernier de la page précédente)
  + limit (optional, integer) - pagination : nombre maximum d'entrées (évenement) à renvoyer pour cette requête

[GET /events/12345678901234?after=1978212345681&limit=2]

Les champs suivants sont obligatoires :

- "uid" (string): identifiant unique de l'évènement chez le fournisseur
- "title" (object): titre de l'évenement. au moins la propriété "fr" (string, le titre en français) doit être indiquée
- "description" (object): description de l'évenement. au moins la propriété "fr" (string, la description en français) doit être indiquée
- "updatedAt" (string): date de dernière mise à jour de l'évenement
- "timings" (string) (array): un objet par occurence/représentation, avec les champs:
     - "uid": identifiant unique de l'occurence/ de la représentation chez le fournisseur
     - "start": date de début de l'occurence
     - "end": date de fin
- "accessibility" (array) Liste d'installations spécifiques disponibles à l'événement. La clé représente un type de handicap, la valeur est une description de l'équipement proposé. Les clés possibles sont les suivantes:
     - "hi": handicap auditif
     - "mi": handicap moteur
     - "pi": handicap psychique
     - "vi": handicap visuel
     - "sl": langage des cible


Le champ "image" n'est pas obligatoire, mais sans image, un évenement n'apparaitra ni dans les recherches ni dans les recommendations de l'algorithme Pass Culture si on ne lui attache pas ensuite manuellement une image ("accroche") dans le portail PRO Pass CUlture.


Catégories disponibles pour les évènements (champs "category", obligatoire, le plus précis possible):
- "museums_and_heritage" : Musées / Patrimoine
    - "museum_tour": Visite libre de musée
    - "museum_guided_tour": Visite guidée de musée
    - "heritage_site_tour": Visite libre de site patrimonial
    - "heritage_site_guided_tour": Visite guidée de site patrimonial
    - "exhibition": Exposition
- "performing_arts" : Spectacle vivant
- "art_practice" : Pratique artistique
- "movie_screening" : Cinéma
- "game" : Jeu, concours
- "meeting" : Dédicace, rencontre, conférence

Les champs optionnels permettant de mieux décrire l'évenement sont recommandés : plus ces champs sont renseignés préciséments, plus l'évenement a de chances d'être recommandé par l'algorithme ou retourné lors d'une recherche.

Le champ optionnel "tags" est libre. Il est recommandé d'y mettre une liste de termes ou noms de personnes pouvant etre utile lors de la recherche ou pour l'algorithme de recommendation. Pour une plus grande efficacité, on peut précéder la valeur d'un nom de propriété [schema.org](http://schema.org). Par exemple, pour un film avec Louis de Funes, on pourra mettre "Louis de Funes", ou "actor:Louis de Funes", le second étant recommandé. Il n'est utile d'indiquer des noms ou termes qui sont déjà présents dans la description ou le titre de l'évenement que si on indique le nom de propriété schema.org correspondant.

Pour la catégorie spectacle vivant "performing_arts", il est recommandé d'indiquer le code selon la nomenclature Entrée Directe / Deelight dans le champ optionnel "eddCode". 

+ Request

+ Response 200 (application/json)

    + Body

            { 
              "total": 23,
              "limit": 20,
              "offset": 20,
              "events": [
                {
                  "uid": "68134833",
                  "title": {
                    "fr": "Place des Enfants : la Bibliothèque + l'Atelier"
                  },
                  "description": {
                    "fr": "Imaginez un endroit où adultes et enfants sont encouragés à partager ensemble des expériences tout en stimulant leur créativité. Entre bibliothèque créative et aire de jeux pédagogique, Place des Enfants est un espace dédié aux enfants de 0 à 10 ans, conçu à partir de leur perspective, où leur est réservé un accueil tout particulier.\n\n_Place des Enfants_ est inspiré de _Room for children_, projet précurseur de Kulturhuset Stadsteatern à Stockholm. Né en 1998, cet espace est en constante évolution et continue de faire école en Suède et à travers le monde.Attention : tout adulte doit être accompagné d’un enfant !\n\n La Bibliotheque\n\nA la scandinave, enlevez vos chaussures en entrant, puis installez-vous dans une cabane pour lire au calme un des ouvrages phares de la littérature suédoise ! Ou encore, laissez les livres vous emporter dans des jeux d’exploration et des énigmes fantastiques. Demandez aux médiateurs qu’ils vous initient à l’Œuf du Dragon ou qu’ils vous confient la mission Expert des mots…\n\n L’Atelier\n\nPeintre, brodeur ou sculpteur en herbe, cet espace vous est dédié. A vos chevalets, fils et pinceaux et autres papiers journaux pour créer les chefs-d’œuvre de demain.Les médiateurs vous guident au milieu de ce studio créatif éphémère.\n\n"
                  },
                  "image": "https://cibul.s3.amazonaws.com/event_place-des-enfants-la-bibliotheque-l-atelier_234488.jpg",
                  "accessibility": [],
                  "updatedAt": "2018-02-26T10:44:20.000Z",
                  "imageCredits": "Illustration Siri Ahmed Backström, Ed. Cambourakis, 2017",
                  "timings": [
                    {
                      "uid": "68134833_1"
                      "start": "2038-03-10T13:00:00.000Z",
                      "end": "2038-03-10T17:00:00.000Z"
                    },
                    {
                      "uid": "68134833_2"
                      "start": "2038-03-11T11:00:00.000Z",
                      "end": "2038-03-11T17:00:00.000Z"
                    },
                    {
                      "uid": "68134833_3"
                      "start": "2038-03-13T13:00:00.000Z",
                      "end": "2038-03-13T19:00:00.000Z"
                    }
                  ],
                  "registration": [],
                  "category": "museums_and_heritage",
                  "tags": [],
                },
                {
                  "uid": "11156936,
                  "title": {
                    "fr": "Expo littérature : Des mondes illustrés"
                  },
                  "description": {
                    "fr": "Les livres participent pleinement à la découverte des mondes qui nous entourent, que ce soit celui des couleurs et des lettres ou encore celui des pays et des différentes cultures. Le livre ouvre aussi les portes de l’imagination et des concepts : le parlé et l’écrit, le concret et l’abstrait ou encore le rêve et la réalité… Et la liste des possibles pourrait continuer sans fin.\n\nL’exposition est composée de 17 citations constituant un hommage à ce que les livres pour enfants apportent à notre vie quotidienne depuis que nous sommes petits. 17 illustrateurs phares de la littérature enfantine suédoise se sont prêtés au jeu en associant une de leur illustration à l’une des citations.  \nIllustrations de Jens Ahlbom, Lena Anderson, Anna Bengtsson, Gunilla Bergström, Ann Forslind, Sara Gimbergsson, Gunna Grähs, Per Gustavsson, Pija Lindenbaum, Barbo Lindgren, Sara Lundberg, Sven Nordqvist, Pernilla Stahlfelt, Cecilia Torudd, Johan Unenge, Emma Virkeet Stina Wirsén."
                  },
                  "image": "https://cibul.s3.amazonaws.com/event_expo-litterature-des-mondes-illustres_854903.jpg",
                  "accessibility": [],
                  "updatedAt": "2018-02-26T10:42:57.000Z",
                  "imageCredits": "Illustration Sara Gimbergsson",
                  "timings": [
                    {
                      "uid": "11156936_1",
                      "start": "2038-03-10T13:00:00.000Z",
                      "end": "2038-03-10T17:00:00.000Z"
                    },
                    {
                      "uid": "11156936_2",
                      "start": "2038-03-11T11:00:00.000Z",
                      "end": "2038-03-11T17:00:00.000Z"
                    }
                  ],
                  "category": "museums_and_heritage",
                  "tags": ["artist:Jens Ahlbom", "artist:Lena Anderson", "artist:Anna Bengtsson", "artist:Gunilla Bergström", "artist:Ann Forslind", "artist:Sara Gimbergsson", "artist:Gunna Grähs", "artist:Per Gustavsson", "artist:Pija Lindenbaum", "artist:Barbo Lindgren", "artist:Sara Lundberg", "artist:Sven Nordqvist", "artist:Pernilla Stahlfelt", "artist:Cecilia Torudd", "artist:Johan Unenge", "artist:Emma Virkeet Stina Wirsén"],
                }
              ]}

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
            
