# Data Contracts

## Présentation

Ce module génère des fichiers YAML conformes à l'[Open Data Contract Standard (ODCS)](https://bitol.io/open-data-contract-standard/) à partir des modèles SQLAlchemy, et permet de les tester contre une base de données locale via le [CLI datacontract](https://github.com/datacontract/datacontract-cli).

La commande Flask CLI `generate_datacontract` (définie dans `commands.py`) introspecte les modèles SQLAlchemy pour produire une représentation YAML conforme à ODCS.

### Fonctionnement

1. **Introspection du modèle** – Pour chaque modèle enregistré, la commande parcourt toutes les colonnes de la table.
2. **Mapping des propriétés du schéma** – Chaque colonne est convertie en `SchemaProperty` contenant :
   - `name` – le nom de la colonne
   - `physicalType` – le type PostgreSQL (ex. `VARCHAR`, `BIGINT`)
   - `logicalType` – un type logique portable dérivé du type Python de la colonne (`string`, `integer`, `number`, `boolean`, `date`, `timestamp`, `time`, `object`, `array`)
   - `required` / `primaryKey` – métadonnées de contraintes
   - `quality` – règles de validation pour les colonnes de type enum (liste des valeurs valides)
3. **Assemblage du contrat** – Les propriétés du schéma sont encapsulées dans un objet `OpenDataContractStandard` avec ses métadonnées (version, statut, serveurs).
4. **Sortie YAML** – Le contrat est sérialisé en YAML et affiché sur stdout.

### Fonctions principales

| Fonction | Rôle |
|---|---|
| `_get_local_server()` | Retourne la configuration du serveur PostgreSQL local |
| `_get_logical_type(python_type)` | Convertit un type Python en type logique |
| `_get_schema_property(column)` | Construit un `SchemaProperty` à partir d'une colonne SQLAlchemy |
| `_get_datacontract_standard(model)` | Assemble le contrat ODCS complet pour un modèle |
| `generate_datacontract()` | Point d'entrée de la commande Flask CLI |

## Tester un data contract en local

### Prérequis

- La stack Docker backend est lancée (`pc-start-backend`)
- Le CLI `datacontract` est installé (`pip install datacontract-cli`)

### Étape 1 – Générer le YAML ODCS

Exécuter la commande Flask dans le conteneur API et rediriger la sortie vers un fichier :

```bash
docker exec pc-api bash -c "cd /usr/src/app/ && flask generate_datacontract" > api/src/pcapi/datacontracts/odcs/offer.yaml
```

### Étape 2 – Convertir au format datacontract

Importer le fichier ODCS au format du CLI datacontract :

```bash
datacontract import --format odcs --source api/src/pcapi/datacontracts/odcs/offer.yaml > api/src/pcapi/datacontracts/offer_dcs.yaml
```

### Étape 3 – Lancer les tests

Tester le contrat contre la base de données locale en fournissant les identifiants PostgreSQL en variables d'environnement :

```bash
DATACONTRACT_POSTGRES_USERNAME=pass_culture \
DATACONTRACT_POSTGRES_PASSWORD=passq \
datacontract test api/src/pcapi/datacontracts/offer_dcs.yaml
```

Le CLI se connecte à la base locale (selon la configuration de la section `servers` du contrat) et vérifie que le schéma réel correspond à la définition du contrat.