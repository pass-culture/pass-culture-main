# PCproxy

Proxy rapide pour exposer des resources privées sans appels à la base de données.

## Installation

Se mettre dans le dossier `proxy` puis:

créer un environement virtuel 

```shell
python3 -m venv pc_env
```

activer l'environnement virtuel 
```shell
source pc_env/bin/activate
```

installer le proxy avec les dépendances de developpement:

```shell
pip install .[dev]
```

lancer le proxy
```shell
fastapi dev src/pcproxy/main.py
```
