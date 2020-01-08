# Package `algolia`

- [Algolia](https://www.algolia.com) ;
- [Documentation Algolia](https://www.algolia.com/doc/api-client/getting-started/install/python/?language=python) ;
- objet = document à indexer.

## api

Fonctions pour discuter avec Algolia.

## rules_engine

Fonction qui détermine si l'offre est éligible à être indexée, dans le cas contraire, on demande à la supprimer de l'index.

## builder

Fonction qui formatte l'objet à indexer.

## orchestrator

Fonction qui indexe ou supprime un objet.

## Tester

```bash
pc python
```

```python
from scripts.algolia_indexing.indexing import indexing
indexing(number_of_offers)
```

ou

```python
from algolia.orchestrator import orchestrate
orchestrate(offer_ids)
```

Deux réponses possible :

- `2019-12-18 12:36:44 INFO     Indexing X objectsID [SQ, ...]`
- `2019-12-18 12:36:44 INFO     Deleting X objectsID [SQ, ...]`
