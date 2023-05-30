# Fournisseur de données Titelive

Description des données récupérées depuis Titelive.

## Titelive Things

Sur le FTP Titelive sont déposés chaque jour un fichier contenant plusieurs informations sur les oeuvres disponibles
dans le réseau de librairies.
Chaque fichier reste disponible pour une durée de 26 jours sur le serveur.
Les fichiers sont tous nommés selon le format : QuotidienJJ.tit (avec JJ le jour de dépôt du fichier).

La documentation avec les informations disponibles dans les fichiers est disponible dans le notion `Titelive Stocks (Epagine / Place des Libraires / Médiacaisse)`

### Code de disponibilité

- 2: Pas encore paru donc à paraître
- 3: Réimpression en cours en revanche nous ne disposons pas d’info sur la date de réimpression
- 4: Non disponible provisoirement il peut s’agir d’une rupture de stock très brève chez le distributeur
  et la référence doit donc en principe être à nouveau disponible dans un délai assez court
- 5: Ne sera plus distribué par nous un distributeur annonce ainsi que cette référence va être bientôt distribué par une
  autre société. Dès que l’on a l’information l’ouvrage passe en disponible avec le nom du nouveau distributeur)
- 6: Arrêt définitif de commercialisation
- 7: Manque sans date code très peu utilisé et équivalent au code 4
- 8: A reparaître donc réédition en cours (NB: en principe la référence est alors rééditée sous un nouveau gencode)
- 9: Abandon de parution

## Type de média

| Indentifiant |                                               Type                                                |
|:------------:|:-------------------------------------------------------------------------------------------------:|
|      A       |                                           AUTRE SUPPORT                                           |
|      BD      |                                          BANDE DESSINEE                                           |
|      BL      |                                           BEAUX LIVRES                                            |
|      C       |                                           CARTE & PLAN                                            |
|      CA      |                                             CD AUDIO                                              |
|      CB      |                                          COFFRET / BOITE                                          |
|      CD      |                                              CD-ROM                                               |
|      CL      |                                            CALENDRIER                                             |
|      DV      |                                                DVD                                                |
|      EB      |                                         CONTENU NUMERIQUE                                         |
|      K7      |                                       CASSETTE AUDIO VIDEO                                        |
|      LA      |                                           LIVRE ANCIEN                                            |
|      LC      |                                         LIVRE + CASSETTE                                          |
|      LD      |                                         LIVRE + CD AUDIO                                          |
|      LE      |                                          LIVRE NUMERIQUE                                          |
|      LR      |                                          LIVRE + CD-ROM                                           |
|      LT      |                                       LISEUSES & TABLETTES                                        |
|      LV      |                                             LIVRE+DVD                                             |
|      M       |                                           MOYEN FORMAT                                            |
|      O       |                                               OBJET                                               |
|      P       |                                               POCHE                                               |
|      PC      |                                        PAPETERIE COLORIAGE                                        |
|      PS      |                                              POSTER                                               |
|      R       |                                               REVUE                                               |
|      T       | Le support TL correspond au format par défaut (c'est-à-dire sans indication précise de l'éditeur) |
|      TL      | Le support TL correspond au format par défaut (c'est-à-dire sans indication précise de l'éditeur) |
|      TR      |                                           TRANSPARENTS                                            |
