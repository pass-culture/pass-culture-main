<details>

<summary> ⏳ Critère X.X - Texte</summary>

**RAWeb/RGAA** : [Critère X.X](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-X-X)
**Ticket** : [PC-XXXXX](https://passculture.atlassian.net/browse/PC-XXXXX)  
**PR** : [#XXXX](https://github.com/pass-culture/pass-culture-main/pull/XXXX)

**Problème** 😱  
Texte

**Correction** 💡  
Texte

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 8.9 - PARTIE 1 - RGAA - Dans chaque page web, les balises ne doivent pas être utilisées uniquement à des fins de présentation ?</summary>

**RAWeb/RGAA** : [Critère 8.9](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-8-9)
**Ticket** : [PC-42854](https://passculture.atlassian.net/browse/PC-42854)  
**PR** : [#24310](https://github.com/pass-culture/pass-culture-main/pull/24310)

**Problèmes** 😱  

_P01 → Tuto de bienvenue (6 étapes)_

Au moins une balise est utilisée uniquement pour créer des effets de présentation.

Par exemple :

- Le texte « Vous pourrez cumuler les deux types d’offres avec un seul compte pass Culture Pro. » est uniquement structuré avec des éléments <div> et <span> (étape 1).
- Le texte « Les jeunes de 15 à 21 ans réservent directement via l'application pass Culture. » est uniquement structuré avec des éléments <div> et <span> (étape 2).
- Le texte « Les jeunes paient avec leur crédit personnel (50€ à 200€). Vous recevez le paiement sous 2 à 3 semaines. » est uniquement structuré avec des éléments <div> et <span> (étape 2).
- Les mêmes constats s’appliquent à l’étape 3 (l’étape 4 étant correctement structurée avec des balises <p>).
- Les éléments du bloc « 3 étapes simples avant d’être visible sur le pass Culture » (page « Comment fonctionne l’inscription ? ») sont implémentés à l’aide de simples éléments <div> sans structure de liste sémantique.

_P02 → Inscription et validation_

Au moins une balise est utilisée uniquement pour créer des effets de présentation.

Par exemple :

- Les textes "Prenez connaissance des modalités" et "Acceptation des conditions et protection des données" sont uniquement structurés avec des <div>. Même chose pour le texte "Email non reçu ?" (étape de confirmation)

_P04 → Inscription structure (3 étapes et validation)_

Au moins une balise est utilisée uniquement pour créer des effets de présentation.

Par exemple :

- Le texte "Vous êtes un équipement d’une collectivité ou d’un établissement public ?" est uniquement structuré avec des <div>.
- Les textes de la fenêtre "Profil"
- Le texte "Coordonnées GPS importantes Les coordonnées GPS permettent aux jeunes de géolocaliser votre offre dans l'application."
- Le texte "Vous pourrez cumuler les deux types d'offres avec un seul compte pass Culture Pro."
- Le texte "Vous pourrez modifier ces informations à tout moment depuis votre espace partenaire."


**Correction** 💡  

Pour _P01 → Tuto de bienvenue (6 étapes)_:

- Remplacement des balises <div> et <span> utilisées pour structurer du contenu textuel par des balises de type <p>, afin de respecter la sémantique du contenu dans les composants concernés
- Transformation du composant `ui-kit/InfoPanel` en `ui-kit/InfoPanelList`, dans les pages concernées :
  - Utilisation une structure de liste sémantique (<ol> et <li>) pour représenter les étapes lorsque le contenu correspond à une séquence d’étapes.
  - Intégration la numérotation directement dans les titres des étapes plutôt que dans des éléments <div> décoratifs, afin de restituer correctement la logique de progression.

Pour _P02 → Inscription et validation_ et _P04 → Inscription structure (3 étapes et validation)_ : 

Déjà traité dans cette PR : [#23954](https://github.com/pass-culture/pass-culture-main/pull/23954)
- Remplacement des balises <div> et <span> par des <p> ou entourez le texte avec des balises <p>, dans le composant `design-system/Banner`



**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 1.2 - RGAA - Chaque image de décoration sans légende est-elle correctement ignorée par les technologies d'assistance ?</summary>

**RAWeb/RGAA** : [Critère 1.2](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-1-2)
**Ticket** : [PC-42844](https://passculture.atlassian.net/browse/PC-42844)
**PR** : [#24226](https://github.com/pass-culture/pass-culture-main/pull/24226)

**Problème** 😱  
TexteP08 → Page d'accueil 

Au moins une image de décoration n'est pas correctement identifiée.

Par exemple : 

- Les images <img alt="Thumbnail for + [IntituleDeLOffre]> du bloc "Offres réservables"
- L’image du logo Adage dans AdagePreviewLayout
- L’image de téléphone dans OfferRecommendationForm

Corrections :

- Pour les images , laisser l'attribut alt vide : alt="".
- Pour toutes les autres images (<svg> notamment) : utiliser une propriété aria-hidden="true".
- Faire un tour général des images et svg de l’application pour voir si toutes les images de décoration sont conformes. 

**Correction** 💡  

- Dans l'aperçu Adage des offres collectives : renommage du `alt` sur le logo ADAGE pour coller au texte de l'image.
- Dans les listes d'offres sur la page d'accueil (offres collectives et individuelles) : les thumbnails ont maintenant un `alt="" aria-hidden="true"`
- Dans toute l'app : ajout de `aria-hidden="true"` sur les `<img alt="" />`


**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critères 10.6 - RGAA - Dans chaque page web, chaque lien dont la nature n'est pas évidente est-il visible par rapport au texte environnant ?</summary>

**RAWeb/RGAA** : [Critère 10.6](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-10-6)
**Ticket** : [PC-42855](https://passculture.atlassian.net/browse/PC-42855)  
**PR** : [#24214](https://github.com/pass-culture/pass-culture-main/pull/24214)

**Problème** 😱

[P11 → Contenus téléchargables](https://integration.passculture.pro/ecoconception/declaration)

Au moins un lien en environnement de texte n'est pas visible par rapport au texte environnant.

Par exemple :

La couleur des liens "passculture.pro " a un rapport de contraste insuffisant par rapport à la couleur du texte environnant.

**Correction** 💡 

Dans les pages https://integration.passculture.pro/ecoconception/declaration et https://integration.passculture.pro/ecoconception/politique :

- On change les liens inline `Button` en `Link`, ce qui ajoute un soulignement et une couleur.

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critères 9.3 - RGAA - Dans chaque page web, chaque liste est-elle correctement structurée ?</summary>

**RAWeb/RGAA** : [Critère 9.3](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-9-3)
**Ticket** : [PC-42855](https://passculture.atlassian.net/browse/PC-42855)  
**PR** : [#24214](https://github.com/pass-culture/pass-culture-main/pull/24214)

**Problème** 😱

[P11 → Contenus téléchargables](https://integration.passculture.pro/ecoconception/declaration)

Au moins un contenu présenté sous forme de liste n'est pas structuré correctement.

Par exemple :

Les contenus présentés sous forme de listes à puces dans le bloc « 6. Frontend – 7 Backend » sont uniquement mis en forme visuellement et ne sont pas structurés comme des listes.

**Correction** 💡 

Dans la page https://integration.passculture.pro/ecoconception/declaration : 

- On restructure tous le document pour que les critères soient sous forme de liste (`<ul>/<li>`). 

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critères 9.1 - RGAA - Dans chaque page web, l'information est-elle structurée par l'utilisation appropriée de titres ?</summary>

**RAWeb/RGAA** : [Critère 9.1](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-9-1)
**Ticket** : [PC-42855](https://passculture.atlassian.net/browse/PC-42855)  
**PR** : [#24214](https://github.com/pass-culture/pass-culture-main/pull/24214)

**Problème** 😱

[P11 → Contenus téléchargables](https://integration.passculture.pro/ecoconception/declaration)

La hiérarchie des titres n'est pas pertinente.

Par exemple : 

Plusieurs sections du contenu sont identifiées uniquement par une mise en forme visuelle (texte en gras), sans utiliser de titre HTML adapté. C'est notamment le cas des intitulés « Évaluation de l’utilité du service, en tenant compte de ses impacts environnementaux », « Cibles utilisatrices de l'espace partenaire du pass Culture », etc.

**Correction** 💡 

Dans la page https://integration.passculture.pro/ecoconception/declaration : 

- Transformation des textes servant d’intitulés de sections en véritables titres HTML avec le niveau de hiérarchie adapté (`<h4>` dans ces cas).

**Retours audit** 🔥  
Texte

</details>

<br>
<details>

<summary> ⏳ Critère 8.9 - RGAA - Dans chaque page web, les balises ne doivent pas être utilisées uniquement à des fins de présentation ?</summary>

**RAWeb/RGAA** : [Critère 8.9](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-8-9)
**Ticket** : [PC-42989](https://passculture.atlassian.net/browse/PC-42989)  
**PR** : [#23954](https://github.com/pass-culture/pass-culture-main/pull/23954)

**Problème** 😱  
P05 → Création offre réservable (5 étapes et confirmation)

Au moins une balise est utilisée uniquement pour créer des effets de présentation.

- Les textes d'encadrés "À savoir" sont uniquement structurés avec des <div>.

- Les textes dans les différents bloc à l'étape "Récapitulatif" (ex : "Votre offre est accessible aux publics en situation de handicap :") et à l'étape "Aperçu"

- Les textes "Votre offre est désormais visible et réservable par les enseignants et chefs d’établissements de l’établissement scolaire : LYCEE MILITAIRE NATIONAL" (étape confirmation de publication)

**Correction** 💡  

Remplacer les balises <div> et <span> par des <p> ou entourez le texte avec des balises <p>.

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 11.6 - RGAA - Dans chaque formulaire, chaque regroupement de champs de formulaire a-t-il une légende ?</summary>

**RAWeb/RGAA** : [Critère 11.6](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-11-6)
**Ticket** : [PC-42863](https://passculture.atlassian.net/browse/PC-42863)  
**PR** : [#23896](https://github.com/pass-culture/pass-culture-main/pull/23896)

**Problème** 😱  
P06 → Création offre individuelle (7 étapes et confirmation)

Au moins un regroupement de champs ne possède pas de légende :

- Le regroupement des champs pour "Horaires pour l’ensemble de ces dates" et "Places et tarifs par horaire" (fenêtre "Définir le calendrier" à l'étape "Horaires et stocks")

- Même chose pour les champs affichés quand l'événement est prévu toutes les semaines

**Correction** 💡  

- Utilisation de l'élément <legend> pour donner un titre aux regroupements créés avec <fieldset>.

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 15.3 - RAWeb - Le contenu généré par chaque transformation des contenus est-il conforme aux règles d’accessibilité numérique ?</summary>

**RAWeb/RGAA** : [Critère 15.3](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-15-3)
**Ticket** : [PC-42867](https://passculture.atlassian.net/browse/PC-42867)  
**PR** : [#23910](https://github.com/pass-culture/pass-culture-main/pull/23910)

**Problème** 😱  
P05 → Création offre réservable (5 étapes et confirmation)
P06 → Création offre individuelle (7 étapes et confirmation)

Les informations d'accessibilité définies depuis l'outil d'édition ne sont pas conservées lors de la génération du contenu final : 

- Lorsqu’un contributeur renseigne un crédit photo lors de l’ajout d’une image, cette information est affichée sur la page de consultation de l’offre, mais elle n’est pas associée sémantiquement à l’image correspondante.

- L’image et son crédit photo sont ainsi traités comme deux éléments indépendants par les technologies d’assistance. 

**Correction** 💡  
- Associer structurellement les informations complémentaires liées à une image à celle-ci dans le contenu généré.

- Utiliser une structure adaptée permettant aux technologies d’assistance d’identifier l’image et sa légende comme un ensemble unique (par exemple une structure de type <figure> associée à un <figcaption>).

- S’assurer que les informations renseignées dans l’outil d’édition sont conservées et correctement restituées dans le contenu publié.

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 11.2 - RGAA - Chaque étiquette associée à un champ de formulaire est-elle pertinente ?</summary>

**RAWeb/RGAA** : [Critère 11.2](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-11-2)
**Ticket** : [PC-42957](https://passculture.atlassian.net/browse/PC-42957)  
**PR** : [#23908](https://github.com/pass-culture/pass-culture-main/pull/23908)

**Problème** 😱  
P05 → Création offre réservable (5 étapes et confirmation)
P06 → Création offre individuelle (7 étapes et confirmation)

Au moins une étiquette de champ de formulaire n'est pas pertinente :

- Le curseur de zoom de l’éditeur d’image est correctement implémenté via un <input type="range">, mais l’information restituée ne permet pas de comprendre clairement le niveau de zoom appliqué (valeur brute sans mise en contexte utilisateur).


**Correction** 💡  

- Fournir une restitution plus explicite de la valeur du zoom, aussi bien visuelle que pour les technologies d’assistance (par exemple en pourcentage : 100 %, 105 %, etc.).

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 11.2 - RGAA - Chaque étiquette associée à un champ de formulaire est-elle pertinente ?</summary>

**RAWeb/RGAA** : [Critère 11.2](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-11-2)
**Ticket** : [PC-42862](https://passculture.atlassian.net/browse/PC-42862)  
**PR** : [#23860](https://github.com/pass-culture/pass-culture-main/pull/23860)

**Problème** 😱  
P06 → Création offre individuelle (7 étapes et confirmation)

Au moins une étiquette de champ de formulaire n'est pas pertinente.

- Dans le tableau de données à l'étape "Horaires et stocks", la première colonne ne possède pas d’intitulé. Elle contient des cases à cocher permettant de sélectionner une ligne (correspondant à une date d’un événement), sans indication explicite du contexte.

- Les cases à cocher ne disposent pas d’un libellé explicite et visible, ce qui empêche de comprendre clairement l’élément sélectionné (ex. ligne 205171).

- Le titre du tableau de données à l'étape "Horaires et stocks" n’est pas pertinent.

**Correction** 💡  
- Ajout d'un intitulé explicite à la première colonne du tableau : checkbox globale + tooltip accessible "Tout sélectionner"

- Pour le tableau, modification du titre pour "Horaires, tarifs et stocks".

- Association de chaque case à cocher à un libellé explicite reprenant l’information de la ligne (date et heure de l’événement).

- Ajout d'un attribut title sur chaque case à cocher reprenant l’intitulé

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 3.1 - RGAA - Dans chaque page web, l'information ne doit pas être donnée uniquement par la couleur ?
</summary>

**RAWeb/RGAA** : [Critère 3.1](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-3-1)
**Ticket** : [PC-42846](https://passculture.atlassian.net/browse/PC-42846)  
**PR** : [#23848](https://github.com/pass-culture/pass-culture-main/pull/23848)

**Problème** 😱  
1. P05 → Création offre réservable (5 étapes et confirmation)

Au moins une information donnée uniquement par la couleur n'a pas d'alternative :

L'indication d'un critère non respecté dans le bloc « Illustrez votre offre » repose uniquement sur un changement de couleur.

2. P06 → Création offre individuelle (7 étapes et confirmation)

Au moins une information donnée uniquement par la couleur n'a pas d'alternative :

Dans la fenêtre modale « Définir le calendrier », à l'étape « Horaires et stocks », lorsque l'événement est défini sur « Toutes les semaines », les cases à cocher personnalisées correspondant aux jours de la semaine se distinguent uniquement par leur couleur pour indiquer si elles sont cochées ou non.

--> Comme vu par mail, le critère est déjà respecté par la présence de la couleur et de la présence d'une bordure.

**Correction** 💡  
1. Ajout d'une icone croix / check pour signifier la validation ou non du critère
2. Epaississement de la bordure dans le cas "sélectionné", pour renforcer la distinction avec le cas "non sélectionné", comme conseillé par mail.

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 11.10 - RGAA - Dans chaque formulaire, le contrôle de saisie est-il utilisé de manière pertinente ?</summary>

**RGAA** : [Critère 11.10](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-11-10)
**Ticket** : [PC-42864](https://passculture.atlassian.net/browse/PC-42864)  
**PR** : [#23850](https://github.com/pass-culture/pass-culture-main/pull/23850)

**Problème** 😱  
P05 → Création offre réservable (5 étapes et confirmation)
P06 → Création offre individuelle (7 étapes et confirmation)

Le contrôle de saisie n'est pas pertinent :

Les messages d'indication ne sont pas correctement reliés à leur champ respectif. (les blocs "À savoir")

**Correction** 💡  
Relier tous les messages d'aides qui apparaissent à proximité des champs par la relation aria-describedby="id".

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 1.3 - Pour chaque image porteuse d'information ayant une alternative textuelle, cette alternative est-elle pertinente ?</summary>

**RAWeb** : [Critère 1.3](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-1-3)
**Ticket** : [PC-42845](https://passculture.atlassian.net/browse/PC-42845)  
**PR** : [#23755](https://github.com/pass-culture/pass-culture-main/pull/23755)

**Problème** 😱  
Au moins une alternative d'image porteuse d'information n'est pas pertinente.

Le composant <canvas aria-label="Editeur d’image"> dans la fenêtre modale « Modifier une image » (suite à l’import d’une image) dispose d’un aria-label insuffisamment précis. Celui-ci ne décrit pas de manière explicite la fonction réelle du composant, à savoir un éditeur de cadrage permettant de repositionner et recadrer l’image.

**Correction** 💡  
Modifier le aria-label afin de décrire plus précisément la fonctionnalité réelle du composant par "Editeur de cadrage et de zoom de l'image".

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 16.2 - RAWeb - Le service d’assistance répond aux besoins de communication des personnes handicapées directement ou par l’intermédiaire d’un service de relais ?</summary>

**RAWeb** : [Critère 16.2](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-16-2)
**Ticket** : [PC-42868](https://passculture.atlassian.net/browse/PC-42868)  
**PR** : [#23715](https://github.com/pass-culture/pass-culture-main/pull/23715)

**Problème** 😱  
Le support d'accessibilité ne répond pas aux emails envoyés à l'adresse fournie sur la Déclaration d'Accessibilité.

**Correction** 💡  
L'adresse était inaccessible par le support - nous y avons maintenant l'accès. 

**Retours audit** 🔥  
TBD

</details>

<br>

<details>

<summary> ⏳ Critère 10.9 - RGAA - Dans chaque page web, l'information ne doit pas être donnée uniquement par la forme, taille ou position ?</summary>

**RAWeb** : [Critère 10.9](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-10-9)
**Ticket** : [PC-42860](https://passculture.atlassian.net/browse/PC-42860)  
**PR** : [#23701](https://github.com/pass-culture/pass-culture-main/pull/23701)

**Problème** 😱  
Sur la page « Inscription structure», l'indication « étape en cours», positionnée hors écran, est placée en dehors de la balise `<a>`. Elle n'est donc pas associée au lien et risque de ne pas être restituée lors d'une navigation par les liens

**Correction** 💡  
Ajout de l'aria-label sur les liens du nouveau composant DS Stepper + un aria-current="step" sur la balise `<li>` contenant le lien.

**Retours audit** 🔥  
TBD

</details>


<details>

<summary> ⏳ Critère 8.9 - Dans chaque page web, les balises ne doivent pas être utilisées uniquement à des fins de présentation ?</summary>

**RAWeb/RGAA** : [Critère 8.9](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-8-9)
**Ticket** : [PC-42990](https://passculture.atlassian.net/browse/PC-42990)  
**PR** : [#23997](https://github.com/pass-culture/pass-culture-main/pull/23997)

**Problème** 😱  

Au moins une balise est utilisée uniquement pour créer des effets de présentation.

P07 → Informations bancaires 

- Le texte "Espace administration".
- Le texte "Démarche Numérique est une plateforme sécurisée de démarches administratives en ligne qui permet de déposer votre dossier de compte bancaire."

P08 → Page d'accueil

- ~~Les textes "Expire aujourd'hui", "Prévu le ...", "publiée", etc. du bloc "'Offres réservables".~~ => Corrigé dans #23954
- ~~Le texte "Aucun compte bancaire configuré pour percevoir vos remboursements" du bloc "Remboursement"~~ => Corrigé dans #23954

P09 → Les offres

- Le texte "XX offres"

- P10 → Les réservations

- ~~Le texte "Télécharger vos réservations dans l’onglet “Données d’activité” de votre Espace administration accessible en haut à droite."~~ => Corrigé dans #23954

P13 → Les offres réservables (collectif)

- ~~Le texte "Télécharger vos offres réservables dans l’onglet “Données d’activité” de votre Espace administration accessible en haut à droite."~~ => Corrigé dans #23954


**Correction** 💡  
Remplacer les balises `<div>` et `<span>` par des `<p>` ou entourez le texte avec des balises `<p>`.

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 5.3 - RGAA - Pour chaque tableau de mise en forme, le contenu linéarisé reste-t-il compréhensible ?</summary>

**RAWeb** : [Critère 5.3](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-5-3)
**Ticket** : [PC-42847](https://passculture.atlassian.net/browse/PC-42847)  
**PR** : [#23998](https://github.com/pass-culture/pass-culture-main/pull/23998)

**Problème** 😱  
Les informations ne se présentent pas dans un ordre logique de lecture pour au moins un tableau de présentation.
- En version responsive, le tableau "Horaires et stocks" n'est plus un tableau de donnée

**Correction** 💡  
Pour le tableau, ajouter le role="presentation" sur la balise `<table>`.

**Retours audit** 🔥  
TBD

</details>

<br>

<details>

<summary> ⏳ Critère 5.5 - RGAA - Pour chaque tableau de données ayant un titre, celui-ci est-il pertinent ?</summary>

**RAWeb** : [Critère 5.5](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-5-5)
**Ticket** : [PC-42847](https://passculture.atlassian.net/browse/PC-42847)  
**PR** : [#23998](https://github.com/pass-culture/pass-culture-main/pull/23998)

**Problème** 😱  
Au moins un titre de tableau de données n'est pas pertinent.

- ~~P06 → Création offre individuelle : Le titre du tableau de données à l'étape "Horaires et stocks"~~ Corrigé dans #23860
- P09 → Les offres / P10 → Les réservations / P13 → Les offres réservables (collectif) : Le titre du tableau des offres / réservations est “Tableau de données”

**Correction** 💡  
Pour le tableau, ajoute un titre pertinent.

**Retours audit** 🔥  
TBD

</details>

<br>

<details>

<summary> ⏳ Critère 5.8 - RGAA - Chaque tableau de mise en forme ne doit pas utiliser d'éléments propres aux tableaux de données ?</summary>

**RAWeb** : [Critère 5.8](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-5-8)
**Ticket** : [PC-42847](https://passculture.atlassian.net/browse/PC-42847)  
**PR** : [#23998](https://github.com/pass-culture/pass-culture-main/pull/23998)

**Problème** 😱  
Au moins un tableau de mise en forme utilise des éléments propres aux tableaux de données.

- Le tableau qui met en forme le contenu de l'étape "Horaires et stocks" en version responsive
- Vérifier les autres tableaux en version responsive

**Correction** 💡  
Pour tous les tableaux de mise en forme :

Supprimer les balises propres aux tableaux de données <caption>, <th>, <thead>, <tfoot>, <colgroup>.

Supprimer les attributs scope, headers, axis, role="rowheader", role="columnheader".

**Retours audit** 🔥  
TBD

</details>

<br>

<details>

<summary> ⏳ Critère 5.8 - RGAA - Chaque tableau de mise en forme ne doit pas utiliser d'éléments propres aux tableaux de données ?</summary>

**RAWeb** : [Critère 5.8](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-5-8)
**Ticket** : [PC-42847](https://passculture.atlassian.net/browse/PC-42847)  
**PR** : [#23998](https://github.com/pass-culture/pass-culture-main/pull/23998)

**Problème** 😱  
Au moins un tableau de mise en forme utilise des éléments propres aux tableaux de données.

- Le tableau qui met en forme le contenu de l'étape "Horaires et stocks" en version responsive
- Vérifier les autres tableaux en version responsive

**Correction** 💡  
Pour tous les tableaux de mise en forme :

Supprimer les balises propres aux tableaux de données <caption>, <th>, <thead>, <tfoot>, <colgroup>.

Supprimer les attributs scope, headers, axis, role="rowheader", role="columnheader".

**Retours audit** 🔥  
TBD

</details>
<br>

<details>

<summary> ⏳ Critère 5.7 - RGAA - Pour chaque tableau de données, la technique appropriée permettant d'associer chaque cellule avec ses en-têtes est-elle utilisée ?</summary>

**RAWeb** : [Critère 5.7](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-5-7)
**Ticket** : [PC-42850](https://passculture.atlassian.net/browse/PC-42850)  
**PR** : [#24000](https://github.com/pass-culture/pass-culture-main/pull/24000)

**Problème** 😱  
Les cellules de données ne sont pas correctement liées aux cellules d'en-tête pour au moins un tableau de données.

- P10 → Les réservations : Après activation du composant « Détails », une cellule de données (<td colspan="6">) est ajoutée au tableau. Cette cellule contient des informations complémentaires associées à une ligne de données, mais elle s'étend sur l'ensemble des colonnes sans permettre d'identifier clairement les en-têtes auxquels ces informations se rapportent.

- P13 → Les offres réservables (collectif) : Le tableau contient une cellule de données (<td colspan="8">) associée à plusieurs colonnes du tableau. Cette cellule contient des informations complémentaires liées à une ligne de données, mais sa structure ne permet pas d'établir clairement son association avec les différents en-têtes de colonnes.


**Correction** 💡  
Implémenter le tableau comme un tableau de données complexe en définissant explicitement les relations entre les cellules et leurs en-têtes.

**Retours audit** 🔥  
TBD

</details>
<br>

<details>

<summary> ⏳ Critère 7.5 - RGAA - Dans chaque page web, les messages de statut sont-ils correctement restitués par les technologies d'assistance ?</summary>

**RAWeb** : [Critère 7.5](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-7-5)
**Ticket** : [PC-42853](https://passculture.atlassian.net/browse/PC-42853)  
**PR** : [#24158](https://github.com/pass-culture/pass-culture-main/pull/24158)

**Problème** 😱  
Au moins un message de statut n'est pas correctement restitué aux technologies d'assistance.


**Correction** 💡  
- Les blocs avec les rôles status sont maintenant toujours visibles, et le contenu change en fonction de l'alerte ou status à afficher.
- Ajout du rôle status aux blocs représentant des résultats de tableaux vides.

**Retours audit** 🔥  
TBD

</details>
