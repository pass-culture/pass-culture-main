TODO :

Offres qui manquent en staging et dont on a besoin:

- [ ] events avec des dates bookables dans le mois
  - [x] Event à plusieurs dates et horaires (Cinéma)
  - [ ] Evenement à 1 seule date (sans date picker)
  - [ ] Offres duo
  - [ ] Edge case: quand on lance le test le dernier jour du mois

Idées d'amélios:

- [ ] des test géolocalisés en E2E
- [ ] des offres dans différentes villes

---

Notes:

- [x] On lances les tests E2E actuels juste après le rebuild de staging
      On lance `.maestro/tests/ReservationOffreEvenement.yml` qui casse au moment de la recherche d'une offre ciné

- [ ] On lance les fonctions du script 1 par 1 et on voit ce que ça fix:

  - On lance `get_offers_for_each_subcategory(10)` -> Pas de résultat parce qu'on a pas réindexé
  - On réindexe, on relance
  - Le script casse au moment de éserver l'offre: offres expirée, donc non réservable
  - TODO: s'assurer que les offres réindexées dans staging sont toutes _bookables_
    - bookable => `offer.isReleased` and not `offer.isExpired` (i.e. not `hasBookingLimitDatetimesPassed` pour au moins 1 stock)
    - `is_eligible_for_search` suffit

On rencontre le problème suivant:

La query SQLA:

```python
query_naive = (
    offers_models.Offer.query.join(offers_models.Stock)
    .join(offerer_models.Venue)
    .join(offerer_models.Offerer)
    .filter(
        offers_models.Offer.is_eligible_for_search,
        offers_models.Offer.subcategoryId == "SEANCE_CINE",
    )
    .limit(10)
)
```

Le résultat retourne _somehow_ des offres non actives (as in, offer.isActive == False)
Pistes de solution:

- décortiquer le `is_eligible_for_search` en `filters` plus "bas niveau"
- Investiguer sur la query SQL qui est output
