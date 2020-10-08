# Fournisseur de données Titelive

Description des données récupérées depuis Titelive.


## Titelive Things

Sur le FTP Titelive sont déposés chaque jour un fichier contenant plusieurs informations sur les oeuvres disponibles dans le réseau de librairies.
Chaque fichier reste disponible pour une durée de 26 jours sur le serveur.
Les fichiers sont tous nommés selon le format : QuotidienJJ.tit (avec JJ le jour de dépôt du fichier).

Voici la liste des informations disponibles dans ces fichiers :


|  Position   | Information | Obligatoire | Description  |
| :-------:   |:-----------:|:-----------:| :-------------------|
| 0           | ean13       | -           | Code barre à 13 chiffres |
| 1           | isbn        | non           | Numéro international numérisé du livre |
| 2           | titre        | oui           | long max 250, Obligatoire, En minuscules accentuées |
| 3           | titre_court        | oui           | Variable/max 250	Obligatoire	inutile pour exploitation sur un site marchand |
| 4           | code_csr        | oui           | Il s'agit des codes RAYON (voir table de correspondance) |
| 5           | code_dispo        | oui           | cf. partie Code de disponibilité plus bas dans le document |
| 6           | collection        | -           | Variable/max 160	Oui si collection	En minuscules accentuées |
| 7           | num_in_collection        | non           | Variable/max 5	facultatif ( vide )	Numéro du titre au sein de la collection (pour le poche et les revues) |
| 9           | prix        | oui           | décimal / 2 chiffres après la virgule	Obligatoire	Prix public éditeur (TTC) |
| 10          | editeur        | oui           | Variable /max 40	Obligatoire	En capitales sans accent |
| 11          | distributeur        | oui           | En capitales sans accent |
| 12          | date_parution        | oui           | jj/mm/aaaa	Obligatoire	01/01/2070 si inconnue |
| 13          | code_support        | oui           | Variable/max 2 caractères  voir table de correspondance SUPPORT (par exemple, poche). Le support TL correspond au format par défaut (c'est-à-dire sans indication précise de l'éditeur) |
| 14          | code_tva        | oui           | entier sur un chiffre	Obligatoire	voir table de correspondance TVA |
| 15          | n_pages        | non           | entier ( par défaut 0 ) |
| 15          | n_pages        | non           | entier ( par défaut 0 ) |
| 16          | longueur       | non |  décimal / 1 chiffre après la virgule	Facultatif ( par défaut 0 )	en centimètres |
| 17          | largeur        | non |  décimal / 1 chiffre après la virgule	Facultatif ( par défaut 0 )	en centimètres |
| 18          | epaisseur      | non |  décimal / 1 chiffre après la virgule	Facultatif ( par défaut 0 )	en centimètres |
| 19          | poids      | non |  entier	Facultatif ( par défaut 0 )	en grammes |
| 21          | is_update      | - |  entier de valeur 0 ou 1	0=Création,1=Modif	indique s'il s'agit d'un nouvelle fiche ou d'une fiche mise-à-jour mais déjà connue |
| 23          | auteurs        | oui |  Obligatoire	En minuscules accentuées |
| 24          | datetime_created       | oui |  jj/mm/aaaa hh:mm:ss	Obligatoire	création de la fiche (inutile pour exploitation de l'info sur un site marchand) |
| 25          | date_updated       | oui |  jj/mm/aaaa hh:mm:ss	Obligatoire	dernière mise à jour de la fiche (inutile pour exploitation de l'info sur un site marchand) |
| 26          | taux_tva       | oui |  décimal / deux chiffres après la virgule	Obligatoire |
| 27          | libelle_csr        | oui |  Variable  / max 80	Obligatoire	Libellé du rayon |
| 28          | traducteur         | non |  Facultatif ( par défaut vide )	En minuscules accentuées |
| 29          | langue_orig        | non |  Facultatif ( par défaut vide ) |
| 31          | commentaire        | non |  Facultatif	information qui complète le titre (sous-titre, edition collector, etc.) |
| 32          | classement_top         | - |  Entier	Toujours si au Top 200	indication relative aux meilleures ventes de livre en France (1 signifie que le titre est classé n°1 au Top 200 de la semaine). |
| 33          | has_image      | oui |  entier de valeur 0 ou 1	Obligatoire	1 si référence avec image |
| 34          | code_edi_fournisseur       | oui |  13 caractères	Obligatoire	numéro utile pour les commande EDI |
| 35          | libelle_serie_bd       | non |  Facultatif |
| 38          | ref_editeur        | non |  12 caractères	Facultatif	référence interne aux éditeurs, utilisé en scolaire |
| 39          | is_scolaire        | oui |  entier de valeur 0 ou 1	Toujours	permet d'identifier les ouvrages scolaires ; 0 : non ; 1 : oui |
| 40          | n_extraits_mp3         | oui |  Entier	Toujours	nombre d'extraits sonores associés à la réf |
| 41          | url_extrait_pdf        | non |  Facultatif ( par défaut vide )	extrait pdf de l'oeuvre |
| 42          | id_auteur      | non |  Entier	Facultatif ( par défaut vide )	permet de faire le lien entre l'auteur et sa biographie |
| 43          | indice_dewey       | non |  Facultatif ( par défaut vide ) |
| 44          | code_regroupement      | oui |  Entier	Obligatoire	permet de faire le lien entre les mêmes œuvres ; 0 si non regroupé |


### Code de disponibilité
+ 2: Pas encore paru donc à paraître
+ 3: Réimpression en cours en revanche nous ne disposons pas d’info sur la date de réimpression
+ 4: Non disponible provisoirement il peut s’agir d’une rupture de stock très brève chez le distributeur
 et la référence doit donc en principe être à nouveau disponible dans un délai assez court
+ 5: Ne sera plus distribué par nous un distributeur annonce ainsi que cette référence va être bientôt distribué par une autre société. Dès que l’on a l’information l’ouvrage passe en disponible avec le nom du nouveau distributeur)
+ 6: Arrêt définitif de commercialisation
+ 7: Manque sans date code très peu utilisé et équivalent au code 4
+ 8: A reparaître donc réédition en cours (NB : en principe la référence est alors rééditée sous un nouveau gencode)
+ 9: Abandon de parution


## Type de média

|  Indentifiant   | Type |
| :-------:   |:-----------:|
| A           | AUTRE SUPPORT      |
| BD           | BANDE DESSINEE      |
| BL           | BEAUX LIVRES      |
| C           | CARTE & PLAN     |
| CA           | CD AUDIO    |
| CB           | COFFRET / BOITE    |
| CD           |  CD-ROM      |
| CL           | CALENDRIER      |
| DV           | DVD      |
| EB           | CONTENU NUMERIQUE      |
| K7           | CASSETTE AUDIO VIDEO      |
| LA           | LIVRE ANCIEN      |
| LC           | LIVRE + CASSETTE     |
| LD           | LIVRE + CD AUDIO     |
| LE           | LIVRE NUMERIQUE     |
| LR           | LIVRE + CD-ROM      |
| LT           | LISEUSES & TABLETTES      |
| LV           | LIVRE+DVD      |
| M           | MOYEN FORMAT      |
| O           | OBJET      |
| P           | POCHE     |
| PC           |  PAPETERIE COLORIAGE      |
| PS           | POSTER     |
| R           | REVUE     |
| T           |  Le support TL correspond au format par défaut (c'est-à-dire sans indication précise de l'éditeur)      |
| TL           | Le support TL correspond au format par défaut (c'est-à-dire sans indication précise de l'éditeur)   |
| TR           | TRANSPARENTS     |
