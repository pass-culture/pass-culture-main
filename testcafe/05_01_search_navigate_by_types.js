import { ClientFunction, Selector, RequestMock } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { hasSignedUpUser93 } from './helpers/users'
import { ROOT_PATH } from '../src/utils/config'

const getPageUrl = ClientFunction(() => window.location.href.toString())

const getSearchResultsHook = RequestMock()
  .onRequestTo(`${ROOT_PATH}recherche/resultats/Applaudir?categories=Applaudir`)
  .respond([], 200, { 'access-control-allow-origin': '*' })

const searchResultsTitle = Selector('#results-title')

fixture('O5_01_01 Recherche | Je ne suis pas connecté·e').page(
  `${ROOT_PATH}recherche`
)

test('Je suis redirigé vers la page /connexion', async t => {
  await t.expect(getPageUrl()).contains('/connexion', { timeout: 500 })
})

fixture(
  "O5_01_02 Recherche | Je me suis connecté·e | J'arrive sur la page de recherche | Header"
).beforeEach(async t => {
  await t
    .useRole(createUserRole(hasSignedUpUser93))
    .navigateTo(`${ROOT_PATH}recherche`)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/recherche')
})

const headerTitle = Selector('header')
const toogleFilterButton = Selector('#search-filter-menu-toggle-button').find(
  'img'
)

test('Je vois le titre de la page', async t => {
  await t.expect(headerTitle.textContent).eql('Recherche')
})

test('Je ne vois pas le bouton retour', async t => {
  await t.expect(Selector('button.back-button').exists).notOk()
})

test('Je vois le champ de recherche par mot-clé', async t => {
  await t
  await t.expect(Selector('#search-page-keywords-field').exists).ok()
})

test("Le filtre de recherche existe et l'icône n'est pas activé", async t => {
  await t
    .expect(toogleFilterButton.getAttribute('src'))
    .contains('ico-filter.svg')
})

test('Je vois le titre de la recherche par catégories', async t => {
  const title = Selector('#nav-by-offer-type').find('h2')
  await t.expect(title.innerText).eql('PAR CATÉGORIES')
})

test('Je vois 7 vignettes', async t => {
  const pictureButton = Selector('#button-nav-by-offer-type')
  await t.expect(pictureButton.count).eql(7)
})

test('Je vois 1 vignette  ', async t => {
  const searchPicture = Selector('.search-picture')
  const searchPicture2 = searchPicture.nth(0).find('img')
  await t
    .expect(searchPicture2.getAttribute('src'))
    .contains('/icons/img-Applaudir.png')

    .expect(searchPicture.innerText)
    .eql('Applaudir')
})

test('Lorsque je clique sur la croix, je reviens à la page des offres', async t => {
  const closeButton = Selector('#search-close-button')

  await t
    .click(closeButton)
    .wait(500)
    .expect(getPageUrl())
    .contains('/decouverte', { timeout: 3000 })
})

fixture(
  "O5_01_03 Recherche | Je cherche des offres par catégories et j'ai des résultats"
).beforeEach(async t => {
  const buttonNavByOfferType = Selector('#button-nav-by-offer-type').withText(
    'Lire'
  )
  await t
    .useRole(createUserRole(hasSignedUpUser93))
    .navigateTo(`${ROOT_PATH}recherche/`)
    .click(buttonNavByOfferType)
    .wait(500)
})

test("Je clique sur la vignette 'Lire' et je suis redirigé vers la page de résultats de la recherche", async t => {
  const backButton = Selector('button.back-button')
  await t
    .expect(getPageUrl())
    .contains('/recherche/resultats/Lire', { timeout: 3000 })

    // Le titre du header change
    .expect(headerTitle.textContent)
    .eql('Recherche : résultats')

    // Le filtre apparaît comme activé
    .expect(toogleFilterButton.getAttribute('src'))
    .contains('ico-filter-active')

  // Je vois le bouton pour revenir à la home
  await t
    .expect(backButton.exists)
    .ok()

    // Je clique sur le bouton pour revenir à la home
    .click(backButton)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}recherche`, { timeout: 3000 })
})

test('Je vois le header de la page de résultats de la catégorie Lire', async t => {
  const resultsHeader = Selector('#nav-results-header')
  const category = Selector('#category-description')
  const categoryTitle = category.find('h2')
  // Je vois l'en-tête de la page de résultats
  const categoryDescription = category.find('span')
  await t

    .expect(resultsHeader.getStyleProperty('background-image'))
    .contains('/icons/img-Lire-L.jpg')

    .expect(categoryTitle.innerText)
    .eql('Lire')

    .expect(categoryDescription.innerText)
    .eql(
      'S’abonner à un quotidien d’actualité ? À un hebdomadaire humoristique ? À un mensuel dédié à la nature ? Acheter une BD ou un manga ? Ou tout simplement ce livre dont tout le monde parle ?'
    )
})

test('Je vois les résultats de la page de résultats de la catégorie Lire', async t => {
  const resultsSection = Selector('.search-results').nth(0)
  const imgResult = Selector('.search-results')
    .nth(0)
    .find('img')
  const linkResult = Selector('.search-results')
    .nth(0)
    .find('a')

  await t
    .expect(searchResultsTitle.innerText)
    .eql('')
    .expect(resultsSection.exists)
    .ok()
    .expect(resultsSection.find('h5').exists)
    .ok()
    .expect(Selector('#recommendation-date').exists)
    .ok()
    .expect(imgResult.getAttribute('src'))
    .contains('/storage/thumbs/mediations/')

    .click(linkResult)

  await t.expect(getPageUrl()).contains('/decouverte', { timeout: 500 })
})

fixture(
  "O5_01_04 Recherche | Je cherche des offres par catégories et je n'ai de résultats"
).requestHooks(getSearchResultsHook)

const button = Selector('#button-nav-by-offer-type').withText('Applaudir')
const resultsHeader = Selector('#nav-results-header')
const category = Selector('#category-description')
const categoryTitle = category.find('h2')
// Je vois l'en-tête de la page de résultats
const categoryDescription = category.find('span')

test('Je vois le header de la page de résultats de la catégorie Lire', async t => {
  await t
    .useRole(createUserRole(hasSignedUpUser93))
    .navigateTo(`${ROOT_PATH}recherche/`)
    .click(button)
    .wait(500)

    .expect(resultsHeader.getStyleProperty('background-image'))
    .contains('/icons/img-Applaudir-L.jpg')

    .expect(categoryTitle.innerText)
    .eql('Applaudir')

    .expect(categoryDescription.innerText)
    .eql(
      'Suivre un géant de 12 mètres dans la ville ? Rire aux éclats devant un stand up ? Rêver le temps d’un opéra ou d’un spectacle de danse ? Assister à une pièce de théâtre, ou se laisser conter une histoire ?'
    )
})

test("Je vois un titre de la section des résultats qui m'informe qu'il n'y a pas de résultats", async t => {
  await t
    .useRole(createUserRole(hasSignedUpUser93))
    .navigateTo(`${ROOT_PATH}recherche/`)
    .click(button)
    .wait(500)
    .expect(getPageUrl())
    .contains('/recherche/resultats/Applaudir?categories=Applaudir', {
      timeout: 3000,
    })

  await t
    .expect(searchResultsTitle.innerText)
    .eql("IL N'Y A PAS D'OFFRES DANS CETTE CATÉGORIE POUR LE MOMENT.")
})

fixture('O5_01_05 Recherche | Footer')

const menuButton = Selector('#open-menu-button')
const mainMenu = Selector('#main-menu')

test("Lorsque je clique sur l'icône profil, la modale s'affiche", async t => {
  await t
    .useRole(createUserRole(hasSignedUpUser93))
    .navigateTo(`${ROOT_PATH}recherche/`)
    .click(menuButton)
    .wait(100)
    .expect(mainMenu.visible)
    .ok()
    .expect(mainMenu.hasClass('entered'))
    .ok()
})
