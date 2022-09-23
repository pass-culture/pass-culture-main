# Package `scheduled_tasks`

Les modules de ce package contiennent des tâches à exécution régulières.

## Do
Un autre décorateur `@log_cron_with_transaction` permet de logguer l'exécution des crons sous un format standard afin de profiter des outils de monitoring.

Exemple :
```python
@log_cron_with_transaction
def synchronize_titelive_stocks(app):
    titelive_stocks_provider_id = get_provider_by_local_class(TITELIVE_STOCKS_PROVIDER_NAME).id
    update_venues_for_specific_provider(titelive_stocks_provider_id)
```

### Logging

Le fichier `logger.py`, concentre les fonctions permettant de définir les règles d'affichages des logs concernant l'exécution des crons.
3 status sont définis : `STARTED`, `ERROR` et `ENDED`, pour nous permettre de valider la bonne exécution de ces tâches.


### Feature Flipping
Par convention, la plupart sinon tous les crons sont feature flippé. Cela permet d'activer ou désactiver dynamiquement leur prochaine exécution.
Le paramètre de feature associé doit être ajouté à l'enum `FeatureToggle` qui permettra de remplir la table `Feature`.
Un dernier décorateur `@cron_require_feature` permet de vérifier la feature avant l'exécution.

Exemple :
```python
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE)
def synchronize_titelive_stocks(app):
    titelive_stocks_provider_id = get_provider_by_local_class(TITELIVE_STOCKS_PROVIDER_NAME).id
    update_venues_for_specific_provider(titelive_stocks_provider_id)
```

**Attention : ce décorateur doit être le plus proche de la signature de la fonction**

### Do

Exemple :
```python
@cron_context
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE)
def synchronize_titelive_stocks(app):
    titelive_stocks_provider_id = get_provider_by_local_class(TITELIVE_STOCKS_PROVIDER_NAME).id
    update_venues_for_specific_provider(titelive_stocks_provider_id)
```

### Don't

Exemple :
```python
@log_cron_with_transaction
@cron_require_feature(FeatureToggle.SYNCHRONIZE_TITELIVE)
@cron_context
def synchronize_titelive_stocks(app):
    titelive_stocks_provider_id = get_provider_by_local_class(TITELIVE_STOCKS_PROVIDER_NAME).id
    update_venues_for_specific_provider(titelive_stocks_provider_id)
```


## Exécution

En local, il est possible d'exécuter à la main le contenu des fichiers `clock*.py` afin de valider les règles d'enregistrement de ces tâches.
Pour cela, il faut démarrer un backend api, puis :

```bash
pc bash
cd /opt
```
