### Fournisseurs

Ceci décrit l'API à implémenter par les partenaires techniques de Pass Culture qui souhaitent fournir des évènements ou des stocks de manière automatisée. Les trois sections de cet API (/things, /events et /stocks) sont indépendantes et ne sont donc pas nécessairement toutes à implémenter.

Pass Culture s'identifie auprès des partenaires techniques via un certificat client SSL. La clé publique est publiée sur le site Pass Culture, et les partenaires sont prévenus à l'avance en cas de changement de clé via notre liste de diffusion email "partenaires techniques".

#### Les évènements [/events/{siret}]

**Statut actuel : brouillon**

Cette API est apellée immédiatement lorsqu'un offreur culturel vous choisit comme fournisseur dans le portail, puis une fois par nuit et par offreur vous ayant choisi par la suite.

Règles de mise à jour des données dans Pass Culture:
- Si la requête reçoit une réponse, on écrase toutes les données précédentes
- Si pas de retour on essaye une seconde fois, puis une alerte vous est envoyé par mail

+ Parameters

  + siret (optional, string) - Identifiant "siret" du commerce.
  + after (optional, string) - pagination : référence de la dernière entrée (évenement) traitée (le dernier de la page précédente)
  + limit (optional, integer) - pagination : nombre maximum d'entrées (évenement) à renvoyer pour cette requête


###### Lister les évènements pour un établissement [GET /events/12345678901234?after=1978212345681&limit=2]

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
                  "keywords": {
                    "fr": [
                      "exposition",
                      "enfants",
                      "famille",
                      "bibliothèque",
                      "atelier"
                    ]
                  },
                  "image": "https://cibul.s3.amazonaws.com/event_place-des-enfants-la-bibliotheque-l-atelier_234488.jpg",
                  "age": {
                    "min": 0,
                    "max": 10
                  },
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
                  "contributor": {},
                  "category": "Event.PerformingArts,
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
                  "keywords": {
                    "fr": [
                      "exposition",
                      "littérature",
                      "familles"
                    ]
                  },
                  "image": "https://cibul.s3.amazonaws.com/event_expo-litterature-des-mondes-illustres_854903.jpg",
                  "age": null,
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
                  "contributor": {},
                  "category": null,
                  "tags": [],
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


Catégories disponibles pour les évènements (champs "category"): 
- "museum_heritage" : Musées / Patrimoine
- "performing_arts" : Spectacle vivant
- "art_practice" : Pratique artistique
- "movie_screening" : Cinéma
- "music" : Musique
- "game" : Jeu

Un évenement ou une date qui était présent(e) dans un appel précédent mais ne l'est plus est considéré comme étant à suprimmer du Pass Culture.

#### Les Stocks [/stocks/{siret}]

**Statut actuel : protype, pour implémentations pilotes**

Cette API est apellée immédiatement lorsqu'un offreur culturel vous choisit comme fournisseur dans le portail, puis une fois par nuit et par offreur vous ayant choisi par la suite.

Règles de mise à jour des données dans Pass Culture:
- Si la requête reçoit une réponse, on écrase toutes les données précédentes
- Si pas de retour on essaye une seconde fois, puis une alerte vous est envoyé par mail
- Si pas de retour après 2 jours, on efface toutes les données (tous les stocks à 0), mais les appels continuent.


+ Parameters

  + siret (optional, string) - Identifiant "siret" du lieu de l'évenement.
  + modifiedSince (optional, string) - date au format 2012-04-23T18:25:43.511Z. L'API ne renvoie que les évenements modifiés depuis cette date
  + after (optional, string) - pagination : EAN13 de la dernière entrée traitée (le dernier de la page précédente)
  + limit (optional, integer) - pagination : nombre maximum d'entrées à renvoyer pour cette requête
  
  

###### Lister les stocks disponible pour un établissement [GET /stocks/12345678901234?after=1978212345681&limit=2]

Les références renvoyées (ref) sont les EAN13 du code barre du produit pour les objets. Pour les d'évènements, ref est l'identifiant (uid) de l'occurence (timing).

L'ordre est au choix du fournisseur mais ne doit pas varier entre deux requetes.

"total" représente le nombre total d'entrées (nombre de références donc, ou presque, cf. le sujet du prix ci-dessous) disponibles.
"limit" indique le nombre d'entrées maximum retournées pour une requete. Il est inférieur ou égal au paramètre limit envoyé dans la requete (inférieur si le serveur souhaite limiter, égal sinon)
"offset" représente le nombre d'entrées précedent celles qui sont présentées

Dans une entrée,
- "available" est le stock disponible pour la référence "ref" pour un objet. C'est le nombre de places disponibles pour un évenement.
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
