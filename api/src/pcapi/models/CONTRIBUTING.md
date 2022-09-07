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

#### Transmettre un Feature Flag à l'app jeune

Lorsqu'on a besoin d'utiliser un Feature Flag sur l'app jeune, il faut transmettre le Feature Flag via l'endpoint [`/settings`](https://github.com/pass-culture/pass-culture-main/blob/d4eeed54c82aa616f10473198518b636c8e19d3c/api/tests/routes/native/v1/settings_test.py#L24)

Pour que cet ajout soit mis à disposition dans le contrat d'interface généré par Swagger pour l'app native, il faut également l'ajouter à la classe de SettingsResponse dans le serializer de settings.py

### Supprimer un Feature Flag

1. Enlever toute utilisation du flag
2. Enlever la ligne de FeatureToggle
3. Ajouter une [action post-mep](https://www.notion.so/passcultureapp/Manip-faire-pour-les-MES-MEP-MEI-1e3c8bc00b224ca18852be1d717c52e5) pour enlever le Flag de la db (`delete from feature where name='xxx'`) après le prochain déploiement.
