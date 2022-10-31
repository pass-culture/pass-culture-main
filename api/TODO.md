# Tout doux

[US](https://passculture.atlassian.net/browse/PC-17881)

[Graph](https://github.com/pass-culture/pass-culture-app-native/blob/chantier-cta/user_status.mmd)

[Mob Time](https://mobtime.hadrienmp.fr/mob/pass-culture)

* [ ] has_to_complete_subscription
* [ ] has_subscription_pending
* [ ] has_subscription_issues

sous statuts d'éligible

* subscriptionStatus
  * has_to_complete_subscription
    * Si le champ nextSubscriptionStep de la route /subscription/next_step n'est pas null => état has_to_complete_subscription
  * has_subscription_pending
    * get_identity_check_subscription_status -> pending
  * has_subscription_issues
    * subscription message is not None
    * Corentin voudrait vérifier des trucs
      * certains "KO" peuvent etre corrigés, d'autres non, donc ça serait non_ellible ?

[liste des messages](https://miro.com/app/board/o9J_lkIEN5c=/)
