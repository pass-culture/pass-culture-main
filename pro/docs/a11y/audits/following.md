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