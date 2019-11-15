### Fournisseurs

Ceci décrit l'API à implémenter par les partenaires techniques de Pass Culture qui souhaitent fournir des évènements ou des stocks de manière automatisée. Les trois sections de cet API (/things, /events et /stocks) sont indépendantes et ne sont donc pas nécessairement toutes à implémenter.

#### Les évènements [/events/{siret}]

**Statut actuel : brouillon**

Cette API est apellée immédiatement lorsqu'un offreur culturel vous choisit comme fournisseur dans le portail, puis une fois par nuit et par offreur vous ayant choisi par la suite.

Règles de mise à jour des données dans Pass Culture:
- Si la requête reçoit une réponse, on écrase toutes les données précédentes
- Si pas de retour on essaye une seconde fois, puis une alerte vous est envoyé par mail
- Un évenement ou une occurence (date) future qui figurait dans un appel précédent mais ne figure plus pour ce lieu est considéré comme étant à ne plus afficher dans Pass Culture. S'il y a déjà des réservations dans Pass Culture pour cet évennement ou cette date, les réservations seront anullées.

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

Pour la catégorie spectacle vivant "performing_arts", il est recommandé d'indiquer le code selon la nomenclature Entrée Directe / Deelight dans le champ optionnel "eddCode". Il s'agit d'un entier correspondant au genre et sous-genre:
- 100	Arts de la rue		
    - 101			Carnaval
    - 102			Fanfare
    - 103			Mime
    - 104			Parade
    - 105			Théâtre de Rue
    - 106			Théâtre Promenade
- 200	Cirque / Magie		
    - 201			Cirque Contemporain
    - 202			Cirque Hors les murs
    - 203			Cirque Traditionel
    - 204			Cirque Voyageur
    - 205			Clown
    - 206			Hypnose
    - 207			Mentaliste
    - 208			Spectacle de Magie
    - 209			Spectacle Équestre
- 300	Danse		
    - 301			Danse du Monde
    - 302			Ballet
    - 303			Cancan
    - 304			Claquette
    - 305			Classique
    - 306			Contemporaine
    - 307			Danse du Monde
    - 308			Flamenco
    - 309			Moderne Jazz
    - 311			Salsa
    - 312			Swing
    - 313			Tango
    - 314			Urbaine
- 400	Humour / Café-théâtre		
    - 401			Café Théâtre
    - 402			Improvisation
    - 403			Seul.e en scène
    - 404			Sketch
    - 405			Stand Up
    - 406			Ventriloque
- 500	Musique		
    - 501		Jazz	
        - 502			Acid Jazz
        - 503			Avant-Garde Jazz
        - 504			Bebop
        - 505			Big Band
        - 506			Blue Note 
        - 507			Cool Jazz
        - 508			Crossover Jazz
        - 509			Dixieland
        - 510			Ethio Jazz
        - 511			Fusion
        - 512			Jazz Contemporain
        - 513			Jazz Funk
        - 514			Mainstream
        - 515			Manouche
        - 516			Traditionel
        - 517			Vocal Jazz
        - 518			Ragtime
        - 519			Smooth
    - 520		Blues	
        - 521			Blues Accoustique
        - 522			Blues Contemporain
        - 523			Blues Électrique
        - 524			Blues Rock
        - 525			Chicago Blues
        - 526			Classic Blues
        - 527			Country Blues
        - 528			Delta Blues
        - 529			Ragtime
    - 530		Reggae	
        - 531			2-Tone
        - 532			Dancehall
        - 533			Dub
        - 534			Roots 
        - 535			Ska
        - 536			Zouk 
    - 600		Classique	
        - 601			Avant-garde
        - 602			Baroque
        - 603			Chant
        - 604			Chorale
        - 605			Contemporain
        - 606			Expressioniste
        - 607			Impressioniste
        - 608			Médievale
        - 609			Minimaliste
        - 610			Moderne 
        - 611			Oratorio
        - 612			Opéra
        - 613			Renaissance
        - 614			Romantique
    - 700		Musique du Monde	
        - 701			Africaine
        - 702			Afro Beat
        - 703			Afro Pop
        - 704			Alternativo 
        - 705			Amérique du Nord
        - 706			Amérique du Sud
        - 707			Asiatique
        - 708			Baladas y Boleros
        - 709			Bossa Nova
        - 710			Brésilienne
        - 711			Cajun
        - 712			Calypso
        - 713			Caribéenne
        - 714			Celtique
        - 715			Cumbia 
        - 716			Flamenco
        - 717			Grècque
        - 718			Indienne
        - 719			Latin Jazz
        - 720			Moyen-Orient
        - 721			Musique Latine Contemporaine
        - 722			Nuevo Flamenco
        - 723			Pop Latino
        - 724			Portuguese fado 
        - 725			Rai
        - 726			Salsa
        - 727			Tango Argentin
        - 728			Yiddish
    - 800		Pop	
        - 801			Britpop
        - 802			Bubblegum 
        - 803			Dance Pop
        - 804			Dream Pop 
        - 805			Electro Pop
        - 806			Indie Pop
        - 808			J-Pop
        - 809			K-Pop
        - 810			Pop Punk 
        - 811			Pop/Rock
        - 812			Power Pop 
        - 813			Soft Rock
        - 814			Synthpop 
        - 815			Teen Pop
    - 820		Rock	
        - 821			Acid Rock 
        - 822			Arena Rock
        - 823			Art Rock
        - 824			College Rock
        - 825			Glam Rock
        - 826			Grunge
        - 827			Hard Rock
        - 828			Indie Rock
        - 829			Lo-fi
        - 830			Prog-Rock
        - 831			Psychedelic
        - 832			Rock & Roll
        - 833			Rock Experimental
        - 834			Rockabilly
        - 835			Shoegaze
        - 836			Rock Electro
    - 840		Metal	
        - 841			Black Metal
        - 842			Death Metal 
        - 843			Doom Metal
        - 844			Gothic 
        - 845			Metal Core
        - 846			Metal Progressif
        - 847			Trash Metal
        - 848			Metal Industriel
        - 849			Fusion
    - 850		Punk	
        - 851			Post Punk 
        - 852			Hardcore Punk
        - 853			Afro Punk
        - 854			Grindcore
        - 855			Noise Rock 
    - 860		Folk	
        - 861			Folk Contemporaine
        - 862			Indie Folk
        - 863			Folk Rock
        - 864			New Acoustic
        - 865			Folk Traditionelle
        - 866			Tex-Mex
    - 870		Country	
        - 871			Country Alternative
        - 872			Americana
        - 873			Bluegrass
        - 874			Country Contemporaine
        - 875			Gospel Country
        - 876			Country Pop
    - 880		Electro	
        - 881			Bitpop
        - 882			Breakbeat 
        - 883			Chillwave
        - 884			Dance
        - 885			Downtempo
        - 886			Drum & Bass 
        - 887			Dubstep
        - 888			Electro Experimental
        - 889			Electronica
        - 890			Garage
        - 891			Grime
        - 892			Hard Dance
        - 893			Hardcore
        - 894			House
        - 895			Industriel
        - 896			Lounge
        - 897			Techno
        - 898			Trance
    - 900		Hip-Hop/Rap	
        - 901			Bounce
        - 902			Hip Hop
        - 903			Rap Alternatif
        - 905			Rap East Coast
        - 906			Rap Français
        - 907			Rap Gangsta
        - 908			Rap Hardcore
        - 909			Rap Latino
        - 910			Rap Old School
        - 911			Rap Underground
        - 912			Rap West Coast
        - 913			Trap
        - 914			Trip Hop
        - 921			R&B Contemporain
        - 922			Disco
        - 923			Doo Wop
        - 924			Funk
        - 925			Soul
        - 926			Motown
        - 927			Neo Soul
        - 928			Soul Psychedelique
    - 930		Gospel	
        - 931			Spiritual Gospel
        - 932			Traditional Gospel
        - 933			Southern Gospel
        - 934			Contemporary Gospel
        - 935			Bluegrass Gospel
        - 936			Blues Gospel
        - 937			Country Gospel
        - 938			Hybrid Gospel
    - 1000		Chansons / Variétés	
        - 1001			Musette
        - 1002			Chanson Française
        - 1003			Music Hall
        - 1004			Folklore français
        - 1005			Chanson à texte
        - 1006			Slam
- 1100	Spectacle Musical / Cabaret / Opérette		
    - 1101			Cabaret
    - 1102			Café Concert
    - 1103			Claquette
    - 1104			Comédie Musicale
    - 1105			Opéra Bouffe
    - 1108			Opérette
    - 1109			Revue
    - 1111			Burlesque
    - 1112			Comédie-Ballet
    - 1113			Opéra Comique
    - 1114			Opéra-Ballet
    - 1115			Théâtre musical
- 1200	Spectacle Jeunesse		
    - 1201			Conte
    - 1202			Théâtre jeunesse
    - 1203			Spectacle Petite Enfance
    - 1204			Magie Enfance
    - 1205			Spectacle pédagogique
    - 1206			Marionettes
    - 1207			Comédie musicale jeunesse
    - 1208			Théâtre d'Ombres
- 1300	Théâtre		
    - 1301			Boulevard
    - 1302			Classique
    - 1303			Comédie
    - 1304			Contemporain
    - 1305			Lecture
    - 1306			Spectacle Scénographique
    - 1307			Théâtre Experimental
    - 1308			Théâtre d'Objet
    - 1309			Tragédie
- 1400	Pluridisciplinaire		
    - 1401			Performance
    - 1402			Poésie
- 1500	Autre (spectacle sur glace, historique, aquatique, …)  		
    - 1501			Son et lumière
    - 1502			Spectacle sur glace
    - 1503			Spectacle historique
    - 1504			Spectacle aquatique

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
