Lien vers le ticket Jira : https://passculture.atlassian.net/browse/PC-XXXXX


## But de la pull request

(Ajout de fonctionnalités, Problèmes résolus, etc)

##  Implémentation

- (Ajouts de modèles, Changements significatifs)
​
##  Informations supplémentaires

- Exemples : nettoyage de code, utilisation de factories, Boy Scout Rule
- Explications sur l'utilisation d'outils peu communs (Exemple psql window function, metaclasses, yield from)
​
## Checklist :

- [ ] La branche est bien nommée et les commits réfèrent le ticket Jira
    - [ ] Branche : pc-XXX-whatever-describe-the-branch
    - [ ] PR : (PC-XXX) Description rapide de l' US
    - [ ] Commit(s) : [PC-XXX] description rapide du ticket
- [ ] J'ai écrit les tests nécessaires
- [ ] J'ai vérifié les migrations (upgrade / downgrade ; locks)
- [ ] J'ai tenté d'améliorer la dette technique (BSR, déplacement de modèles dans `pcapi.core`, etc)
- [ ] J'ai ajouté un / des screenshots pour d'éventuels changements graphiques (ex: Admin)
