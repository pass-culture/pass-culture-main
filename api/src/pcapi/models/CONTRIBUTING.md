# Package `models`

## Feature Flags

Les Feature Flags (ou Feature Toggle) permettent de désactiver / activer une fonctionnalité depuis l'admin (ex: [admin staging](https://backend.staging.passculture.team/pc/back-office/feature/)) sans avoir besoin de déployer de code.

### Installer un nouveau Feature Flag

1. **Ajouter** une ligne dans l'enum `FeatureToggle`

Le flag sera ajouté dans la table `Feature` lors du déploiement, via la méthode `install_feature_flags`

2. Configurer la **valeur par défaut** (ou initiale) du flag.

Si la valeur initiale est `True`, ne rien faire.

Si la valeur initiale est `False`, ajouter une ligne dans le tuple `FEATURES_DISABLED_BY_DEFAULT`.

3. ⚠️ Dans le cas d'utilisation _ajout d'une fonctionnalité activée une fois que les développements sont finis_, **créer un ticket** pour supprimer le feature flag, ou a mininima pour modifier sa valeur initiale, une fois le chantier fini. En effet, cela peut avoir un impact sur :

- la qualité des tests : c'est la valeur par défaut qui est utilisée (sauf si `@override_features` est utilisé)
- les bugs sur l'environnement `testing` : les données sont périodiquement regénérées et les Feature Flag sont alors réinitialisés avec leur valeur par défaut.

### Supprimer un Feature Flag

1. Enlever toute utilisation du flag
2. Enlever la ligne de FeatureToggle
3. Ajouter une [action post-mep](https://www.notion.so/passcultureapp/Manip-faire-pour-les-MES-MEP-MEI-1e3c8bc00b224ca18852be1d717c52e5) pour enlever le Flag de la db (`delete from feature where name='xxx'`) après le prochain déploiement.
