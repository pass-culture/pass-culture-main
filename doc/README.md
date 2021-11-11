# Documentation de l'API Pass Culture

## Installation des outils

```bash
  npm install -g aglio concurrently drakov dredd
```

## Developement

Pour avoir un drakov mock server à http://localhost:3001
et un aglios rendant le htm produit par la doc à http://localhost:3002
(les deux servers reloadent quand vous changez n'importe quel .apib.md dans le folder src):

```bash
  make dev
```

## Construire le fichier doc correspondant

```bash
  make build
```
