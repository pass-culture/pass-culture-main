### Introduction

Le pass Culture est pensé comme une nouvelle infrastructure de service public : nous proposons ainsi aux fournisseurs technologiques du secteur (billetteries, agenda, progiciels de gestion, systèmes de caisse...) de construire des API communes permettant d'ouvrir cette infrastructure au bénéfice de l’écosystème d’innovation du secteur culturel.

### Environnement en production

Les adresses URL de la plateforme en production sont :
+ Portail professionnel : https://pro.passculture.beta.gouv.fr
+ Application web mobile "jeunes" : https://app.passculture.beta.gouv.fr
+ API : https://backend.passculture.beta.gouv.fr

### Environnement d'intégration

Pour tous les acteurs souhaitant tester les fonctionalités de la plateforme avant de publier leurs offres auprès de nos utilisateurs, nous mettons à disposition un environnement d'intégration dont [voici le guide d’utilisation](https://github.com/betagouv/pass-culture-doc/blob/master/src/24_integration.apib.md).

### API disponibles

Dans le cadre de la version bêta de la plateforme, deux API sont aujourd'hui disponibles : 
+ [API contremarque](https://github.com/betagouv/pass-culture-doc/blob/master/src/23_contremarques.apib.md) qui permet de vérifier la validité et de valider une contremarque générée par le pass Culture
+ [API fournisseur](https://github.com/betagouv/pass-culture-doc/blob/master/src/22_fournisseur.apib.md) qui permet d'automatiser la remontée d’offre dans le portail professionel et éviter ainsi de resaisir manuellement toute une programmation ou l’ensemble des stocks d'une librairie

A moyen terme l’objectif est de stabiliser avec les acteurs des versions standardisées de ces API, en y ajoutant l'ensemble des fonctionalités necessaires. Si vous souhaitez participer à cette construction, contactez-nous sur pass@culture.gouv.fr
