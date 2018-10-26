import { ClientFunction, Selector } from 'testcafe'

import regularUser from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

const getPageUrl = ClientFunction(() => window.location.href.toString())

const searchInput = Selector('#keywords')
const keywordsSearchButton = Selector('#keywords-search-button')
const searchTypeCheckbox = Selector('#search-type-checkbox').withText('Lire')
const resultsTitle = Selector('#results-title')

fixture('O5_01 Recherche | Je ne suis pas connecté·e').page(
  `${ROOT_PATH}recherche`
)

test('Je suis redirigé vers la page /connexion', async t => {
  await t
  await t.expect(getPageUrl()).contains('/connexion', { timeout: 500 })
})

fixture.skip('O5_02 Recherche | Après connexion').beforeEach(async t => {
  await t.useRole(regularUser).navigateTo(`${ROOT_PATH}recherche/`)
})

test('Je peux accéder à la page de  /recherche', async t => {
  await t
    .wait(1000)
    .expect(getPageUrl())
    .contains('/recherche', { timeout: 5000 })
})

// HEADER
// TODO Je ne peux pas cliquer sur le bouton 'BACK' .back-button (je ne le vois pas)

// FOOTER
// Si je clique sur le menu, je ne peux pas cliquer sur Recherche

// ------------------------ RECHERCHE PAR MOTS-CLES

// ------------------------ NO RESULTS
fixture.skip('O5_02 Recherche | Recherche textuelle').beforeEach(async t => {
  await t.useRole(regularUser).navigateTo(`${ROOT_PATH}recherche/categories`)
})

// Je vois le filtre par type sous le formulaire de recherche textuelle

test("Je fais une recherche par mots-clés et je n'ai pas de résultats", async t => {
  await t
    .typeText(searchInput, 'fake')
    .click(keywordsSearchButton)
    .wait(500)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/recherche/resultats')
  await t.expect(resultsTitle.innerText).eql('"FAKE" : 0 RÉSULTAT')
})

// TODO
// Si je n'ai pas de résultats, je vois la navigation par type sous le formulaire de recherche textuelle

// ------------------------ NO RESULTS
test("Je fais une recherche par mots-clés et j'ai des résultats", async t => {
  await t
    .typeText(searchInput, 'vhils')
    .click(keywordsSearchButton)
    .wait(500)
  await t.expect(resultsTitle.innerText).eql('"VHILS" : 1 RÉSULTAT')
})

// Si j'ai des résultats, je vois les vignettes

// Si je clique sur l'offre d'une des vignettes, je suis redirigée vers la page découverte de cette offre...

// Si j'ai des résultats : la page de résultats s'affiche, je ne vois pas le filtre par type sous le formulaire de recherche textuelle

// Si je tape un mot-clé, que je clique sur Chercher, le bouton 'Chercher' devient disabled

// Si je clique sur la croix, l'input chercher se vide et l'url ne change pass

// ------------------------ BACK TO SEARCH PAGE
// Après une recherche si je clique sur back, je reviens à la recherche précédante
// si je veux revenir à ma page de début de recherche je clique sur la flêche < back et cela réinitialise tous les filtres

// ------------------------ NAVIGATION PAR TYPE (LIRE, ETC)
fixture.skip('O5_ Recherche | Navigation par catégorie').beforeEach(async t => {
  await t.useRole(regularUser).navigateTo(`${ROOT_PATH}recherche/`)
})

test('Je clique sur la vignette Lire et je suis redirigé vers la page de résultats de la recherche', async t => {
  await t
  const location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/recherche/categories')
    .click(searchTypeCheckbox)
})

// Voir les fonctionnalitées sur https://github.com/betagouv/pass-culture-browser/issues/664

// NAVIGATION PAR FILTRE
// Je fais apparaître et disparaître le menu de filtres
// Je peux faire une recherche détaillée
// par date
// DATE : Soit plusieurs laps de temps OU par une date précise (date picker)
// Je peux selectionner un des 4 distances proposées
// par type, je peux selectionner plusieurs types

// pour tout rénitialiser, il faut cliquer sur la croix dans le form et sur réninitaliser aussi donc

// Tu peux cumuler recherche textuelle + filtrage des résultats, et tu peux appliquer un filtre à toute la base d’offres puis faire une recherche textuelle dans la base filtrée

// in search input, i can delete my search words by clicking in the close icon

// Quand on clique sur le bouton chercher, si le filtre est ouvert, il se referme mais la recherche reste active

// Quand on navigue par type d'offre, dans la page de résultats on peut lire "il n'y pas d'offre pour le moment " sinon "" s'il y a des offres, elles sont affichées

// Le bouton submit search keyword est désactivé si rien n'est écrit

// Après une navigation par type, si on ouvre le filtre puis quand clique sur le bouton back, le filtre se referme est la recherche est réinitialisée.

// ****** SEARCH RESULTS ********* //
// Tronquer le titre dans le résultat de recherche...

// ****** DATE PICKER ********* //
// Quand il choisit une date, les autres sélecteurs de date (Moins de 5 jours, etc) ne peuvent pas être cochés (et sont donc décochés s'ils l'étaient).
