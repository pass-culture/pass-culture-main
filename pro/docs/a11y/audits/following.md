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
