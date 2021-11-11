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

## Indexation des offres en local

Si lorsque je clique sur une offre sur la webapp lancée en local et que j'ai un loader infini, voilà comment résoudre ce problème: 
- Dans `pass-culture-main/api`, ajouter un fichier `.env.local.secret` avec:
```
ALGOLIA_TRIGGER_INDEXATION=1
ALGOLIA_INDEX_NAME=<ton_index>  <= mettre un index custom, ex: 'local_myName' (surtout pas un existant)
ALGOLIA_APPLICATION_ID=testing...H0 <= à trouver dans `.env.development` dans ce repo
ALGOLIA_API_KEY=6a27...636  <= à trouver sur la plateforme Algolia (API Keys > Write API Key)
```
- Relancer `pc sandbox -n industrial`
- Ici, ajouter un fichier `.env.development.local` qui contient: 
```
ALGOLIA_SEARCH_API_KEY=136...0f067 <= à trouver sur la plateforme Algolia (API Keys > Search API Key)
ALGOLIA_INDEX_NAME=<ton_index>
```
- Relancer la webapp, normalement le clic sur une offre devrait maintenant fonctionner

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
On utilise la librairie [react-tracking](https://github.com/NYTimes/react-tracking), développée par le New York Times :
* Usage par HOC ou par React Hook
* Découple la responsabilité Tracking hors des composants et évite les fuites dans l'app
* Platform agnostic (peut-etre utilisé avec Matomo, GA, etc)


### Events
Les Tracking Events sont une des méthodes proposées par Matomo pour mesurer les interactions utilisateurs avec le contenu de notre plateforme qui ne seraient ni des page view, ni des téléchargements.
Typiquement, un event sera utilisé pour mesurer des clicks sur les éléments de nos pages (navbar, boutons, envoi de formulaires, appels AJAX, etc).

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
  withTracking('PageName')
  connect(mapStateToProps, mapDispatchToProps, mergeProps)
)(MyButton)
```

Le HOC `track` (inclus dans `src/components/hocs/withTracking.js`) décore le container d'une `props` `tracking` qui contient les méthodes de tracking que l'on souhaite utiliser.
Il accepte deux arguments :
- premier argument : un objet contenant le nom de la `page` que l'on souhaite mesurer (correspond à la `catégorie` de l'évènement)
- deuxieme argument (optionnel) : un objet contenant une fonction `dispatch` qui sera exécutée à chaque fois qu'un évènement est déclenché.

Par défaut, la mesure des objets sera poussée dans `window.dataLayer[]`, dans notre cas, on souhaite utiliser les fonctions spécifiques à Matomo pour pousser les évènements dans le `dataLayer`. Cela passe par ce second argument et la fonction `dispatch`.

On peut utiliser la fonction `mergeProps` pour combiner les props venant des différentes sources du container (state, dispatch, container).

## Upgrade de la version

La commande `yarn version` va créée un nouveau commit de version, un nouveau tag et la version sera mise à jour sur la page Mentions Légales
```bash
yarn version
# yarn version --new-version x.x.x
```

[Nous Contacter](https://aide.passculture.app/fr/category/18-ans-1dnil5r/)
