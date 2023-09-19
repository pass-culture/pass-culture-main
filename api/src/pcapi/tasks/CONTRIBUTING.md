# Package `tasks`

Ce module contient les tâches cloud Google.

## Files de tâches cloud

A définir :

- dans tous les fichiers d'environnements `.env` dans `api/`
- dans tous les fichiers terragrunt `**/{env}/cloudtasks/terragrunt.hcl` dans le dépôt `pass-culture/infrastructure`

## Tâches cloud

Les tâches cloud sont définies en utilisant le décorateur `@task` de `decorator.py`.

```python
@task(task_queue_name, route_path, deduplicate, delayed_seconds, timeout)
def my_task(payload: object): ...
```

Cette tâche définit deux points d'entrées :

1. une route `POST /route_path` qui, lorsque appelée, appelle `my_task(payload)`
2. `my_task.delay(payload)` qui ajoute une nouvelle tâche à la file `task_queue_name`. Cette tâche, lorsqu'elle est
   dépilée, appelle `POST /route_path`

`deduplicate` et `delayed_seconds` permettent d'appeler très souvent `my_task` mais de ne l'exécuter que tous les
`delayed_seconds`.

_Note :_ puisqu'une nouvelle route doit être installée dans l'application Flask, il faut s'assurer que le fichier
soit bien importé dans le fichier `./__init__.py` !

## Exceptions et ré-essais

Le ré-essai d'une tâche Google est géré par `ExternalAPIException.is_retryable`, ainsi les exceptions finales lancées par
les tâches cloud doivent hériter de `ExternalAPIException`.
