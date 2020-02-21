# Package `scheduled_tasks`

Les modules de ce package contiennent des tâches à exécution régulières.

## Do
Ces fonctions doivent être regroupées par domaine fonctionel : `booking`, `algolia`, etc.
Chacune de ces fonctions seront appelées dans le fichier `clock` correspondant.
Ces fichiers `clock` offrent un découpage technique pour ses crons. Chaque fichier clock possède son propre espace et contexte d'exécution.

Lors de l'ajout de ses tâches via le scheduler, vous devez ajouter en paramètre `app` afin de fournir le contexte en paramètre à la fonction.

Exemple:
```python
scheduler.add_job(synchronize_titelive_stocks, 'cron',
                          [app],
                          id='synchronize_titelive_stocks',
                          day='*', hour='6')
```


Afin que ces fonctions soit exécutées, un décorateur doit être ajouté `@cron_context`. Celui-ci permet de fournir
le contexte de l'application lors de l'exécution.

Exemple :
```python
@cron_required
def synchronize_titelive_stocks(app):
    titelive_stocks_provider_id = get_provider_by_local_class(TITELIVE_STOCKS_PROVIDER_NAME).id
    update_venues_for_specific_provider(titelive_stocks_provider_id)
```


Un autre décorateur permet de logguer l'exécution des crons sous un format standard afin de profiter des outils de monitoring : `@log_cron`

Exemple :
```python
@log_cron
def synchronize_titelive_stocks(app):
    titelive_stocks_provider_id = get_provider_by_local_class(TITELIVE_STOCKS_PROVIDER_NAME).id
    update_venues_for_specific_provider(titelive_stocks_provider_id)
```

### Feature Flipping
Par convention, la plupart sinon tous les crons sont feature flippé. Cela permet d'activer ou désactiver dynamiquement leur prochaine exécution.
Le paramètre de feature associé doit être ajouté à l'enum `FeatureToggle` qui permettra de remplir la table `Feature`.
Un dernier décorateur permet de vérifier la feature avant l'exécution.

Exemple:
```python
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE)
def synchronize_titelive_stocks(app):
    titelive_stocks_provider_id = get_provider_by_local_class(TITELIVE_STOCKS_PROVIDER_NAME).id
    update_venues_for_specific_provider(titelive_stocks_provider_id)
```

**Attention: ce décorateur doit être le plus proche de la signature de la fonction**
