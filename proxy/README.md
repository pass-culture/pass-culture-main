# PCproxy

Proxy rapide pour exposer des resources privées sans appels à la base de données.

## Installation

Se mettre dans le dossier `proxy` puis:

Créer un environement virtuel 

```shell
python3.13 -m venv pcproxy_env
```

Activer l'environnement virtuel 
```shell
source pcproxy_env/bin/activate
```

Installer le proxy avec les dépendances de developpement:

```shell
pip install ".[dev]"
```

Lancer le proxy
```shell
fastapi dev src/pcproxy/main.py
```

Lancer les tests
```shell

```