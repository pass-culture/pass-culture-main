## Debt-collector ([documentation externe](https://github.com/gael-boyenval/debt-collector))

### Utilisation
> :warning: Sometimes debt-collector get stuck in a detached branche.
When it finish, you may have to checkout the branch you were on.

debt-collector create debt report in three ways:
* on github: a comment on each PR with points recap per changed files
* on a dev branch: a details report, for each rules in each changed files
* on master: a report.html that render a graph with points changes by rule for last 10 release

```shell
# check change on a branch compare to master
# "debt:walk": "debt-collector walk -c ./.debt-collector/config.js -n 10"
yarn debt:check:changed
# create report.html about last 10 releases
# "debt:check:changed": "debt-collector check -c ./.debt-collector/config.js -s master",
yarn debt:walk
```

## Configuration

* Le workflow github pour poster les commentaire est [disponible ici](../../.github/workflows/debt-collector-pro.yml)
* Les regles de validation du code sont définies dans [config.js](./config.js)
