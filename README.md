# pass-culture-browser

[![Coverage Status](https://coveralls.io/repos/github/betagouv/pass-culture-browser/badge.svg?branch=master)](https://coveralls.io/github/betagouv/pass-culture-browser?branch=master)

C'est la version (browser) de l'application frontend du pass Culture.

Il faut aller voir le README dans https://github.com/betagouv/pass-culture-main
pour être informé des différentes lignes de commande associées à ce repo.

## Note sur Yarn

Yarn est prometteur, on vous conseille de l'utiliser. Tâchez de l'installer globalement sur votre ordinateur (https://yarnpkg.com/en/docs/install), puis:

```bash
yarn
```

## Variables d'environnements

A la racine de webapp créer un fichier `env.local`<br>
Les variables disponibles pour l'application sont décrites dans le fichier `src/utils/config.js`

## Tests

#### Tests Unitaires (Jest/Enzyme)

Lancer tous les tests
```bash
yarn test:unit
# Lancer les tests unitaires en local en mode rafraichissement auto
# yarn test:unit --watchAll
```

Lancer un seul fichier en mode watch
```bash
./node_modules/.bin/jest --env=jsdom ./<path>/tests/<fichier> --watch
# yarn test:unit ./path/to/file.spec.js --watch
```

#### Tests Fonctionnels/E2E (Testcafe)

Lancer tous les tests
```bash
pc reset-all-db
pc sandbox --name=industrial
yarn test:cafe
```

Lancer un seul fichier en ligne de commande depuis un environnement local
```bash
./node_modules/.bin/testcafe chrome ./testcafe/02_signin.js
```

## Tracking (avec Matomo)

### Initialisation

Pour être en mesure d'utiliser les fonctionnalités offertes par Matomo, nous devons injecter un script dans le code HTML de notre page index.
Une fois exécuté, il permet d'installer des cookies sur le navigateur de l'usager.
Par défaut, il ne remonte pas beaucoup d'informations. Pour plus de précisions, il faudra lui adjoindre des fonctions (voir ci-après).

### CNIL

> **ATTENTION**: Le code fourni par Matomo ne respecte pas totalement la règlementation française sur la vie privée

Afin d'être en règle, ajouter ce snippet au début du script de Matomo : 
```javascript
<!-- CODE CNIL OBLIGATOIRE -->
_paq.push([function() {
    var self = this;
    function getOriginalVisitorCookieTimeout() {
        var now = new Date(),
        nowTs = Math.round(now.getTime() / 1000),
        visitorInfo = self.getVisitorInfo();
        var createTs = parseInt(visitorInfo[2]);
        var cookieTimeout = 33696000; // 13 mois en secondes
        var originalTimeout = createTs + cookieTimeout - nowTs;
        return originalTimeout;
    }
    this.setVisitorCookieTimeout(getOriginalVisitorCookieTimeout());
}]);
<!-- FIN DU CODE CNIL -->
```

### React-tracking
On utilise la librairie react-tracking, développée par le New York Times :
* Usage par HOC ou par React Hook
* Découple la responsabilité Tracking hors des composants et évite les fuites dans l'app
* Platform agnostic (peut-etre utilisé avec Matomo, GA, etc)


### Events
Les Tracking Events sont une des méthodes proposées par Matomo pour mesurer les interactions utilisateurs avec le contenu de notre plateforme qui ne seraient ni des page view, ni des téléchargements.
Typiquement, un event sera utilisé pour mesurer des clicks sur les éléments de nos pages (menus, boutons, envoi de formulaires, appels AJAX, etc).

Un évènement est constitué de 4 éléments : 
* Catégorie
* Action
* Nom (optionel mais recommendé)
* Valeur (optionel)

Exemple de déclaration d'évènement (fonction `trackEvent`) lorsque l'usager consulte (action : `Consult`), une Offre (catégorie : `Offer`) dont le nom (id) est 'B4' (name: `B4`)  : 
```javascript
_paq.push(['trackEvent', 'Offer', 'Consult', 'B4']);
```
Cet exemple ne comporte pas de valeur, mais si on le souhaitait, on pourrait l'ajouter à la suite du dernier élément du tableau.

### Usage
Si l'on se réfère à la cible archi front, la responsabilité de déclencher un évènement en fonction d'une action utilisateur incombe au composant graphique, à l'aide d'une fonction fournie par son container.
Il est de la responsabilité du container de wrapper l'action du déclenchement de l'event dans cette fonction.

Exemple de container : 

```javascript
const mapStateToProps = state => {
  const somethingId = selectSomethingId(state)
  return {
    somethingId,
  }
}

const mapDispatchToProps = dispatch => ({
  someDispatch: () => dispatch(something()),
})

const mergeProps = (stateProps, dispatchProps, ownProps) => {
  const {
    somethingId,
  } = stateProps
  return {
    ...stateProps,
    ...dispatchProps,
    ...ownProps,
    trackButtonClick: () => {
      ownProps.tracking.trackEvent({ action: 'buttonClick', name: somethingId })
    }
  }
}

export default compose(
  track({ page: 'Offer' }, { dispatch: data => {
    window._paq.push(['trackEvent', data.page, data.action, data.name])
  }}),
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(MyButton)
```

Le HOC `track` décore le container d'une `props` `tracking` qui contient les méthodes de tracking que l'on souhaite utiliser.
Il peut accepter une fonction `dispatch` qui sera exécutée à chaque fois qu'un évènement est déclenché.
On peut utiliser la fonction `mergeProps` pour combiner les props venant des différentes sources du container (state, dispatch, container).

## Upgrade de la version

La commande `yarn version` va créée un nouveau commit de version, un nouveau tag et la version sera mise à jour sur la page Mentions Légales
```bash
yarn version
# yarn version --new-version x.x.x
```

## Font Icons (Fontello)

#### Ajout d'icones

- Ouvrir le site [Fontello.com](https://fontello.com)
- Glisser/Déposer le fichier `public/static/fontello/config.json` dans la page du navigateur
- Ajouter une/des icônes
- Cliquer sur `Download webfont (n)`
- Remplacer et committer le fichier `public/static/fontello/config.json`

#### Mise à jour

La commande ci-dessous permet de mettre à jour le dossier dans `public/static/fontello` avec la dernière configuration à jour
```bash
yarn fontello
```

[Nous Contacter](https://aide.passculture.app/fr/category/18-ans-1dnil5r/)
