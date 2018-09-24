import { ClientFunction, Selector } from 'testcafe'

import regularUser from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

const getPageUrl = ClientFunction(() => window.location.href.toString())

const searchInput = Selector('#search-input')
const keywordsSearchButton = Selector('#keywords-search-button')
const searchTypeCheckbox = Selector('#search-type-checkbox').withText('Lire')
// const refreshKeywordsButton = Selector('#refresh-keywords-button')
// const searchResults = Selector('#search-results')
// const resultsTitle = Selector('#results-title')

fixture('O5_01 Recherche | Je ne suis pas connecté·e').page(
  `${ROOT_PATH}recherche`
)

test('Je suis redirigé vers la page /connexion', async t => {
  await t
  await t.expect(getPageUrl()).contains('/connexion', { timeout: 5000 })
})

fixture('O5_02 Recherche | Après connexion').beforeEach(async t => {
  await t.useRole(regularUser).navigateTo(`${ROOT_PATH}recherche/`)
})

test('Je peux accéder à la page /recherche', async t => {
  await t
  await t.expect(getPageUrl()).contains('/recherche', { timeout: 5000 })
})

fixture.skip('O5_02 Recherche | Recherche textuelle').beforeEach(async t => {
  await t.useRole(regularUser).navigateTo(`${ROOT_PATH}recherche/`)
})

test("Je fais une recherche par mots-clés et je n'ai pas de résultats", async t => {
  await t.typeText(searchInput, 'fake').click(keywordsSearchButton)
})

// si j'ai zéro résultats, je peux voir les vignettes de filtre par catégorie

fixture.skip('O5_ Recherche | Recherche par catégorie').beforeEach(async t => {
  await t.useRole(regularUser).navigateTo(`${ROOT_PATH}recherche/`)
})

test('Je clique sur la vignette Lire et je suis redirigé vers le résultat de la recherche', async t => {
  await t
  const location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/recherche/categories')
    .click(searchTypeCheckbox)
})

// Je clique sur le menu vs navigateTo()

// RECHERCHE TEXTUELLE
// Je peux faire une recherche textuelle
// Je vois le filtre par type sous le formulaire de recherche textuelle
// Si j'ai des résultats : la page de résultats s'affiche, je ne vois pas le filtre par type sous le formulaire de recherche textuelle
// Si je n'ai pas de résultats, je vois le filtre par type sous le formulaire de recherche textuelle
// Si je clique sur la croix, cela efface la selection, si je veux revenir à ma page de début de recherche je clique sur la flêche < back et cela réinitialise tous les filtres

// FILTRE
// Je fais apparaître et disparaître le menu de filtres
// Je peux faire une recherche détaillée
// par date
// DATE : Soit plusieurs laps de temps OU par une date précise (date picker)
// Je peux selectionner un des 4 distances proposées
// par type, je peux selectionner plusieurs types

// pour tout rénitialiser, il faut cliquer sur la croix dans le form et sur réninitaliser aussi donc

// Tu peux cumuler recherche textuelle + filtrage des résultats, et tu peux appliquer un filtre à toute la base d’offres puis faire une recherche textuelle dans la base filtrée
