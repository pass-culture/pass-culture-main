import { ClientFunction, Selector } from 'testcafe'

import { youngUserRole } from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

const getPageUrl = ClientFunction(() => window.location.href.toString())

fixture('O5_01 Recherche | Je ne suis pas connecté·e').page(
  `${ROOT_PATH}recherche`
)

test('Je suis redirigé vers la page /connexion', async t => {
  await t.expect(getPageUrl()).contains('/connexion', { timeout: 500 })
})

fixture(
  "O5_02 Recherche | Je me suis connecté·e | J'arrive sur la page de recherche | Header"
).beforeEach(async t => {
  await t.useRole(youngUserRole).navigateTo(`${ROOT_PATH}recherche/`)
})

const toogleFilterButton = Selector('#search-filter-menu-toggle-button').find('img')
const headerTitle = Selector('header')

test('Je peux accéder à la page de /recherche', async t => {
  await t
    .wait(1000)
    .expect(getPageUrl())
    .contains('/recherche', { timeout: 5000 })
})

// HEADER
test('Lorsque je clique sur la croix, je reviens à la page des offres', async t => {
  const closeButton = Selector('#search-close-button')

  await t
    .click(closeButton)
    .wait(500)
    .expect(getPageUrl())
    .contains('/decouverte', { timeout: 5000 })
})

test('Je vois le titre de la page', async t => {
  await t
    .expect(headerTitle.innerText)
    .eql('Recherche\n')
})

test('Je ne vois pas le bouton retour', async t => {
  await t
  await t.expect(Selector('button.back-button').exists).notOk()
})

test("Le filtre de recherche n'est pas activé", async t => {
  await t
  .expect(toogleFilterButton.getAttribute('src')).contains('ico-filter.svg')
})

fixture(
  'O5_03 Recherche | Je cherche des offres par catégories et navigue'
).beforeEach(async t => {
  await t.useRole(youngUserRole).navigateTo(`${ROOT_PATH}recherche/`)
})

test("Je vois 7 vignettes", async t => {
  // TODO Revoir
  const pictureButton = Selector('#button-nav-by-offer-type')
  await t.expect(pictureButton.count).eql(7)
})

// j'ai des résultats de recherche
test("Je clique sur la vignette 'Lire' et je suis redirigé vers la page de résultats de la recherche", async t => {
  const buttonNavByOfferType = Selector('#button-nav-by-offer-type').withText(
    'Lire'
  )

  await t
    .click(buttonNavByOfferType)
    .expect(getPageUrl())
    .contains('/recherche/resultats/Lire', { timeout: 5000 })

    // Le titre du header change
    .expect(headerTitle.innerText)
    .eql('Recherche : résultats\n')

    // Le filtre apparaît comme activé
    .expect(toogleFilterButton.getAttribute('src')).contains('ico-filter-active')

    // Je vois le bouton pour revenir à la home
    await t.expect(Selector('button.back-button').exists).ok()
})

// Je n'ai pas de résultats

// TODO:
// - contient le search by keywords
// const searchInput = Selector('#keywords')
// const keywordsSearchButton = Selector('#keywords-search-button')
// Page avec résultats
// const resultsTitle = Selector('#results-title')

// Page sans résultat

// FILTRE activable ->
// <div id="search-filter-menu-toggle-button" class="flex-0 text-center flex-rows flex-center pb12 filters-are-opened"><button type="button" class="no-border no-background no-outline "><img alt="ico-chevron-up" src="http://localhost:3000/icons/ico-chevron-up.svg"></button></div>

// Je vois la vignette lire qui est selectionnée 'checked'

// FOOTER
// Si je clique sur le menu, je ne peux pas cliquer sur Recherche
