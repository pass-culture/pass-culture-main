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

<summary> ⏳ Critère 7.5 - Dans chaque page web, les messages de statut sont-ils correctement restitués par les technologies d'assistance ?</summary>

**RAWeb/RGAA** : [Critère 7.5](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-7-5)
**Ticket** : [PC-43948](https://passculture.atlassian.net/browse/PC-43948)  
**PR** : [#24639](https://github.com/pass-culture/pass-culture-main/pull/24639)

**Problème** 😱  
Un élément avec le rôle alert est bien présent pour signaler qu’un des critères de validation n’est pas respecté lors de l’import d’une image. Cependant, cet attribut est positionné sur le conteneur regroupant l’ensemble des critères. En conséquence, l’intégralité de la liste des critères est annoncée par les technologies d’assistance, y compris ceux qui ne sont pas concernés par l’erreur.

**Correction** 💡  
Positionner le rôle alert uniquement sur les éléments réellement en erreur, afin d’éviter la restitution globale de contenus non pertinents.

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 12.8 - Dans chaque page web, l'ordre de tabulation est-il cohérent ?</summary>

**RAWeb/RGAA** : [Critère 12.8](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-12-8)
**Ticket** : [PC-43895](https://passculture.atlassian.net/browse/PC-43895)  
**PR** : [#24584](https://github.com/pass-culture/pass-culture-main/pull/24584)

**Problème** 😱  
L'ordre de tabulation dans la page n'est pas cohérent. 

Bloc « Frais annexes » à l’étape « Dates et prix » : après avoir sélectionné « Oui », la navigation au clavier passe directement au champ « Prix (en €) » sans atteindre le champ obligatoire « Type de frais annexes ». 

De plus, lorsque ce champ est en erreur, l’activation du bouton « Enregistrer et continuer » ne repositionne pas le focus sur le champ concerné.

**Correction** 💡  
Vérifier et corriger l’ordre de tabulation afin qu’il soit cohérent et permette d’atteindre l’ensemble des éléments interactifs dans l’ordre attendu.

Lorsque des erreurs sont détectées après l’activation de « Enregistrer et continuer », repositionner le focus sur le premier champ en erreur.

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 9.4 - Dans chaque page web, chaque citation est-elle correctement indiquée ?</summary>

**RAWeb/RGAA** : [Critère 9.4](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-9-4)
**Ticket** : [PC-43883](https://passculture.atlassian.net/browse/PC-43883)  
**PR** : [#24510](https://github.com/pass-culture/pass-culture-main/pull/24510)

**Problème** 😱  
Au moins une citation n'est pas correctement identifiée.

- Le texte "la personne handicapée a droit à la compensation des conséquences de son handicap, quels que soient l’origine et la nature de sa déficience, son âge ou son mode de vie."

**Correction** 💡  
- Implémenter le passage de texte "la personne handicapée a droit à la compensation des conséquences de son handicap, quels que soient l’origine et la nature de sa déficience, son âge ou son mode de vie." dans un élément <blockquote>.

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 7.1 - Chaque script est-il, si nécessaire, compatible avec les technologies d'assistance ?</summary>

**RAWeb/RGAA** : [Critère 7.1](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-7-1)
**Ticket** : [PC-43716](https://passculture.atlassian.net/browse/PC-43716)  
**PR** : [#24438](https://github.com/pass-culture/pass-culture-main/pull/24438)

**Problème** 😱  
P05 → Création offre réservable (5 étapes et confirmation)
P06 → Création offre individuelle (7 étapes et confirmation)

Lors du changement d'étape, la page entière est rechargée, ce qui provoque un replacement du focus sur la page entière, provoquant un certain nombre de tabulations avant de revenir à un endroit “naturel” pour le focus dans le formulaire.

**Correction** 💡  
Au changement d’étape, replacer le focus à un endroit “naturel” en arrivant à l'étape suivante / précédente, par exemple sur l’onglet de l'étape active.

Après le changement d'étape, déplacer explicitement le focus vers l'élément actif d'étape en utilisant tabindex="-1".

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 7.1 - Chaque script est-il, si nécessaire, compatible avec les technologies d'assistance ?</summary>

**RAWeb/RGAA** : [Critère 7.1](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-7-1)
**Ticket** : [PC-43629](https://passculture.atlassian.net/browse/PC-43629)  
**PR** : [#24423](https://github.com/pass-culture/pass-culture-main/pull/24423)

**Problème** 😱  
P05 → Création offre réservable (5 étapes et confirmation)
P06 → Création offre individuelle (7 étapes et confirmation)

Le composant « Domaine(s) d’activité » 

- est annoncé comme ouvrant une listbox (aria-haspopup="listbox"), alors que le panneau affiché contient une liste de cases à cocher. Les rôles et attributs ARIA utilisés ne correspondent donc pas au comportement réel du composant.

- Le bouton ouvrant le panneau ne restitue pas son état d'ouverture ou de fermeture (aria-expanded absent).

**Correction** 💡  
- Utiliser des rôles et attributs ARIA adaptés au comportement réel du composant. Dans ce cas, privilégier un panneau contenant des cases à cocher plutôt qu'une listbox, ou implémenter une véritable listbox multisélection si tel est le comportement attendu.

- Restituer l'état du panneau à l'aide de l'attribut aria-expanded sur le bouton d'ouverture.

- Veiller à ce que les attributs ARIA utilisés correspondent à la structure et au comportement effectifs du composant, conformément aux spécifications WAI-ARIA.

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 7.1 - Chaque script est-il, si nécessaire, compatible avec les technologies d'assistance ?</summary>

**RAWeb/RGAA** : [Critère 7.1](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-7-1)
**Ticket** : [PC-43622](https://passculture.atlassian.net/browse/PC-43622)  
**PR** : [#24423](https://github.com/pass-culture/pass-culture-main/pull/24423)

**Problème** 😱  

P09 → Les offres individuelles 
P10 → Les réservations
P13 → Les offres réservables  
P14 → Les offres vitrines

Les boutons de filtre “Statut” permettent d'afficher une liste de filtres, mais leur état d'ouverture n'est pas toujours communiqué aux technologies d'assistance.

Par exemple :

- Le bouton “Statut” situé dans l'en-tête de colonne de la page Réservations n'indique pas si le panneau associé est ouvert ou fermé.
- Le bouton ne possède pas toujours de relation explicite avec le contenu affiché.
- Les filtres “Statut” des listes d'offres réservables et vitrines n'annoncent pas le nombre d'éléments sélectionnés, alors qu'une bulle visuelle l'indique aux utilisateurs voyants.
- Certaines icônes décoratives de boutons de filtre communiquent un texte alternatif inutile.

**Correction** 💡  

- Ajout de `aria-expanded` sur les boutons de filtre afin d'indiquer dynamiquement si le panneau associé est ouvert ou fermé.
- Ajout de `aria-controls` pour associer explicitement les boutons aux panneaux de filtre correspondants.
- Maintien de `aria-describedby` sur les filtres “Statut” des listes d'offres réservables et vitrines, y compris lorsque le panneau est fermé, afin de communiquer le nombre d'éléments sélectionnés.
- Ajout d'un rôle explicite au panneau du composant `MultiSelect` et conservation du design existant du panneau.
- Passage des icônes décoratives des boutons de filtre en `alt=""`.
- Vérification que les valeurs sélectionnées du filtre “Statut” restent communiquées via les champs de sélection.

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 7.1 - RGAA - Chaque script est-il, si nécessaire, compatible avec les technologies d'assistance ?</summary>

**RAWeb/RGAA** : [Critère 7.1](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-7-1)
**Ticket** : [PC-43545](https://passculture.atlassian.net/browse/PC-43545)  
**PR** : [#24432](https://github.com/pass-culture/pass-culture-main/pull/24432)

**Problème** 😱  
P05 → Création offre réservable (5 étapes et confirmation)

P06 → Création offre individuelle (7 étapes et confirmation)

- Le bouton “Créer une offre” communique l'état fermé mais pas l'état ouvert, et devrait être de type disclosure et non pas un menu.

- Les checkbox de jours (modale horaires et stocks) utilisent aria-labelledby mais ne le lient à rien

- BaseDatePicker et BaseTimePicker : la valeur n’est pas annoncée au VoiceOver

**Correction** 💡  

- Communiquer l’état ouvert du bouton “Créer une offre” + passer le composant en bouton/link.

- Les checkbox de jours (modale horaires et stocks) devraient soit lier aria-labelledby à un label, soit ne pas présenter cet attribut

- BaseDatePicker et BaseTimePicker : communiquer la valeur au VoiceOver

**Retours audit** 🔥  
Texte

</details>

<br>

<details>

<summary> ⏳ Critère 9.2 - RAWeb - Dans chaque page web, la structure du document est-elle cohérente ?</summary>

**RAWeb/RGAA** : [Critère 9.2](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-9-2)
**Ticket** : [PC-42856](https://passculture.atlassian.net/browse/PC-42856)  
**PR** : [#24545](https://github.com/pass-culture/pass-culture-main/pull/24545)

**Problème** 😱  
Le lien portant le logo « Pass Culture Pro, l'espace des acteurs culturels » est positionné entre les éléments `<header>` et `<main>`, sans être inclus dans un repère de page.

**Correction** 💡  
Le changement de l'ancien layout vers le nouveau `<FullLayout>` corrige de-facto ce problème, qui était lié à l'ancien `<SignUpLayout>`, le logo étant correctement positionné dans le `<header>` du nouveau layout

**Retours audit** 🔥  
TBD

</details>

<br>

<details>

<summary> ⏳ Critère 10.4 - RAWeb - Dans chaque page web, le texte reste-t-il lisible lorsque la taille des caractères est augmentée jusqu’à 200 %, au moins (hors cas particuliers) ?</summary>

**RAWeb/RGAA** : [Critère 10.4](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#crit-10-4)
**Ticket** : [PC-42858](https://passculture.atlassian.net/browse/PC-42858)  
**PR** : [#24545](https://github.com/pass-culture/pass-culture-main/pull/24545)

**Problème** 😱  
Le contenu de l'en-tête de la page n'est plus affiché à 200 % de zoom, le `<header>` étant masqué (display: none).

**Correction** 💡  
Le changement de l'ancien layout vers le nouveau `<FullLayout>` corrige de-facto ce problème, qui était lié à l'ancien `<SignUpLayout>`. Le `<header>` reste bien visible à 200% de zoom dans le nouveau layout.

**Retours audit** 🔥  
TBD

</details>

<br>

<details>

<summary> ⏳ Critère 15.1 - RAWeb - Chaque outil d’édition permet-il de définir les informations d’accessibilité nécessaires pour créer un contenu conforme aux règles d’accessibilité numérique ?</summary>

**RAWeb** : [Critère 15.1](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#topic-15)
**Ticket** : [PC-42868](https://passculture.atlassian.net/browse/PC-42866)  
**PR** : [#24389](https://github.com/pass-culture/pass-culture-main/pull/24389)

**Problème** 😱  

Impossible d'ajouter un texte alternatif sur les images, il n'est pas lu ailleurs dans l'app. 

P05 : Création offre réservable
P06 : Création offre individuelle
P08 : Page d'accueil
P13 : Les offres réservables (collectif)

**Correction** 💡  
Ajout de la possibilité d'ajouter un texte alternatif sur les images (collectif, individuel et partenaire culturel), ce texte alternatif est restitué.

**Retours audit** 🔥  
TBD

</details>

<br>

<details>

<summary> ⏳ Critère 15.1 & 15.3 - RAWeb - Conformité des contenus générés par les outils d'édition</summary>

**RAWeb** : [Critère 15.1](https://accessibilite.public.lu/fr/raweb1.1/criteres.html#topic-15)
**Ticket** : [PC-42868](https://passculture.atlassian.net/browse/PC-42913)  
**PR** : [#24389](https://github.com/pass-culture/pass-culture-main/pull/24389)

**Problème** 😱  

Impossible d'ajouter une description sur les vidéos ajoutées par les acteurs culturels, ces description devrait être lues dans l'app jeune

P06 : Création offre individuelle

**Correction** 💡  
Ajout de la possibilité d'ajouter une description à l'upload d'une vidéo

**Retours audit** 🔥  
TBD

</details>
