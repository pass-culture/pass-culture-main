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

<summary> ⏳ Critère 1.3 - Pour chaque image porteuse d'information ayant une alternative textuelle, cette alternative est-elle pertinente ?</summary>

**RAWeb** : [Critère 1.3](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-1-3)
**Ticket** : [PC-42845](https://passculture.atlassian.net/browse/PC-42845)  
**PR** : [#23755](https://github.com/pass-culture/pass-culture-main/pull/23755)

**Problème** 😱  
Au moins une alternative d'image porteuse d'information n'est pas pertinente.

Le composant <canvas aria-label="Editeur d’image"> dans la fenêtre modale « Modifier une image » (suite à l’import d’une image) dispose d’un aria-label insuffisamment précis. Celui-ci ne décrit pas de manière explicite la fonction réelle du composant, à savoir un éditeur de cadrage permettant de repositionner et recadrer l’image.

Egalement, 

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

<summary> ⏳ Critère 10.9 - RAWeb - Le service d’assistance répond aux besoins de communication des personnes handicapées directement ou par l’intermédiaire d’un service de relais ?</summary>

**RAWeb** : [Critère 10.9](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-10-9)
**Ticket** : [PC-42915](https://passculture.atlassian.net/browse/PC-42915)  
**PR** : [#23701](https://github.com/pass-culture/pass-culture-main/pull/23701)

**Problème** 😱  
Sur la page « Inscription structure», l'indication « étape en cours», positionnée hors écran, est placée en dehors de la balise `<a>`. Elle n'est donc pas associée au lien et risque de ne pas être restituée lors d'une navigation par les liens

**Correction** 💡  
Ajout de l'aria-label sur les liens du nouveau composant DS Stepper + un aria-current="step" sur la balise `<li>` contenant le lien.

**Retours audit** 🔥  
TBD

</details>
