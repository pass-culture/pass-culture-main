Lien vers le ticket Jira : https://passculture.atlassian.net/browse/PC-XXXXX

## But de la pull request

_Ajout de fonctionnalités, Problèmes résolus, etc_

## Implémentation

- _Exemples: Ajouts de modèles, Changements significatifs_

## Informations supplémentaires

- _Exemples: nettoyage de code, utilisation de factories, Boy Scout Rule_
- _Explications sur l'utilisation d'outils peu communs (ex.: psql window function, metaclasses, yield from)_

## Checklist :

- [ ] La branche est bien nommée et les commits réfèrent le ticket Jira
  - Branche : `pc-XXX-whatever-describe-the-branch`
  - PR : `(PC-XXX) Description rapide de l' US`
  - Commit(s) : `(PC-XXX)[PRO|API|…] description rapide du ticket`
- [ ] J'ai écrit les tests nécessaires
- [ ] J'ai vérifié les migrations (upgrade / downgrade ; locks ; édition de `alembic_version_conflict_detection.txt`)
- [ ] J'ai mis à jour la **sandbox** afin que le développement ou la recette soient facilités
- [ ] J'ai tenté d'améliorer la dette technique (BSR, déplacement de modèles dans `pcapi.core`, etc)
- [ ] J'ai ajouté des screenshots pour d'éventuels changements graphiques (ex: Admin)
