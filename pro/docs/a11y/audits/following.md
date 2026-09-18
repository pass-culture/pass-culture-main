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