# La CI/CD

Nous utilisons les GitHub actions pour la CI et la CD du backend et du front pro.

Les workflows sont divisés en 4 grandes catégories :
- les workflows **d'intégration continue (CI)**, préfixés par `ci_`
- les workflows **de déploiement continu (CD)**, préfixés par `cd_`
- les workflows **partagés dédiés à des services particuliers**, préfixés par le nom du service, par exemple `slack_` ou `docker_`
- les workflows **dédiés aux tests de job et de GitHub actions**, préfixés par `test_`

Au sein de ces catégories, les sous-workflows, ie. les workflows qui sont appelés par d'autres workflows (qui ont la configugration `on: workflow_call`), sont préfixés avec `sub_`.
Par exemple, pour la CI le workflow [`ci_sub_test_changes.yml`](workflows/ci_sub_test_changes.yml) et pour la CD le workflow [`cd_sub_create_release.yml`](workflows/cd_sub_create_release.yml).

## CI

Les 3 workflows principaux sont :
- [`ci_check_pr.yml`](workflows/ci_check_pr.yml) : lance les tests sur les changements apportés au code dans une PR
- [`ci_check_push_on_master.yml`](workflows/ci_check_push_on_master.yml)
    - lance les tests sur les changements apportés à chaque push sur `master`
    - si les tests passent :
        - deploie la nouvelle version du storybook sur [GitHub pages](https://pass-culture.github.io/pass-culture-main)
        - déploie le site de maintenance
        - ajoute le tag RC qui est utilisé lors de la création d'une nouvelle release (voir [`cd_create_major_release.yml`](workflows/cd_create_major_release.yml))
- [`ci_check_pr.yml`](workflows/ci_check_pr.yml) : lance les tests sur les changements apportés à chaque push sur une branche de maintenance (branche de la forme `maint/v*`)

Il y a également 2 workflows pour créer des environnements de preview, qui peuvent être lancés à la demande :
- [`ci_deploy_pr_preview.yml`](workflows/ci_deploy_pr_preview.yml) ([:arrow_forward: lancer le workflow](https://github.com/pass-culture/pass-culture-main/actions/workflows/ci_deploy_pr_preview.yml)): déploie un environnement de preview pour tester fonctionnement les changements apportés par la PR
- [`ci_deploy_storybook_preview.yml`](workflows/ci_deploy_storybook_preview.yml) ([:arrow_forward: lancer le workflow](https://github.com/pass-culture/pass-culture-main/actions/workflows/ci_deploy_storybook_preview.yml)): déploie une preview du storybook

## CD

Il y a 2 workflows de création de release :
- [`cd_create_major_release.yml`](workflows/cd_create_major_release.yml) ([:arrow_forward: lancer le workflow](https://github.com/pass-culture/pass-culture-main/actions/workflows/cd_create_major_release.yml)): crée une nouvelle release à partir du dernier commit taggué comme `rc` sur `master`
- [`cd_create_hotfix_release.yml`](workflows/cd_create_hotfix_release.yml) ([:arrow_forward: lancer le workflow](https://github.com/pass-culture/pass-culture-main/actions/workflows/cd_create_hotfix_release.yml)): crée une nouvelle release de _hot-fix_ à partir du dernier commit sur la branche de maintenance (`maint/v*`) sélectionnée


Il y a 3 workflows de déploiement d'une release:
- [`cd_deploy_production.yml`](workflows/cd_deploy_production.yml) ([:arrow_forward: lancer le workflow](https://github.com/pass-culture/pass-culture-main/actions/workflows/cd_deploy_production.yml)): déploie le tag sélectionné en production
- [`cd_deploy_staging_on_major_release.yml`](workflows/cd_deploy_staging_on_major_release.yml) ([:arrow_forward: lancer le workflow](https://github.com/pass-culture/pass-culture-main/actions/workflows/cd_deploy_staging_on_major_release.yml)): déploie automatiquement sur staging la nouvelle version du code tagguée comme majeur au push du tag
- [`cd_deploy_testing_hourly.yml`](workflows/cd_deploy_testing_hourly.yml) ([:arrow_forward: lancer le workflow](https://github.com/pass-culture/pass-culture-main/actions/workflows/cd_deploy_testing_hourly.yml)): déploie le code de `master` toutes les heures sur testing
