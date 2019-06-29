import { RequestMock, Selector } from 'testcafe'

import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

const getSearchResultsHook = RequestMock()
  .onRequestTo(`${ROOT_PATH}recherche/resultats/Applaudir?categories=Applaudir`)
  .respond([], 200, { 'access-control-allow-origin': '*' })

const headerTitle = Selector('header')
const toggleFilterButton = Selector('#search-filter-menu-toggle-button').find(
  'img'
)
const menuButton = Selector('#open-menu-button')
const mainMenu = Selector('#main-menu')
const button = Selector('#nav-by-offer-type .pc-list button').withText(
  'Applaudir'
)
const resultsHeader = Selector('#nav-results-header')
const category = Selector('#category-description')
const categoryTitle = category.find('h2')
const categoryDescription = category.find('span')

let userRole

fixture('O5_01_01 Recherche | Je ne suis pas connecté·e')

test('Je suis redirigé vers la page /connexion', async t => {
  // when
  await t.navigateTo(`${ROOT_PATH}recherche`)

  // then
  await t.expect(getPageUrl()).contains('/connexion')
})

fixture(
  "O5_01_02 Recherche | Je me suis connecté·e | J'arrive sur la page de recherche | Header"
).beforeEach(async t => {
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_05_search',
      'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
    )
  }

  await t.useRole(userRole).navigateTo(`${ROOT_PATH}recherche`)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/recherche')
})

test('Je vois le titre de la page', async t => {
  await t.expect(headerTitle.textContent).eql('Recherche')
})

test('Je ne vois pas le bouton retour', async t => {
  await t.expect(Selector('.back-link').exists).notOk()
})

test('Je vois le champ de recherche par mot-clé', async t => {
  await t.expect(Selector('#search-page-keywords-field').exists).ok()
})

test("Le filtre de recherche existe et l'icône n'est pas activée", async t => {
  await t
    .expect(toggleFilterButton.getAttribute('src'))
    .contains('ico-filter.svg')
})

test('Je vois le titre de la recherche "EXPLORER LES CATÉGORIES"', async t => {
  const title = Selector('#nav-by-offer-type').find('h2')
  await t.expect(title.innerText).eql('EXPLORER LES CATÉGORIES')
})

test('Je vois 7 vignettes', async t => {
  const pictureButton = Selector('#nav-by-offer-type .pc-list button')
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
  // given
  const closeLink = Selector('header .close-link')

  // when
  await t.click(closeLink).wait(500)

  // then
  await t.expect(getPageUrl()).contains('/decouverte')
})

fixture(
  "O5_01_04 Recherche | Je cherche des offres par catégories et je n'ai de résultats"
)
  .requestHooks(getSearchResultsHook)
  .beforeEach(async t => {
    await t.useRole(userRole).navigateTo(`${ROOT_PATH}recherche/`)
  })

test('Je vois le header de la page de résultats de la catégorie Lire', async t => {
  // when
  await t.click(button).wait(500)

  // then
  await t
    .expect(resultsHeader.getStyleProperty('background-image'))
    .contains('/icons/img-Applaudir-L.jpg')
    .expect(categoryTitle.innerText)
    .eql('Applaudir')
    .expect(categoryDescription.innerText)
    .eql(
      'Suivre un géant de 12 mètres dans la ville ? Rire aux éclats devant un stand up ? Rêver le temps d’un opéra ou d’un spectacle de danse ? Assister à une pièce de théâtre, ou se laisser conter une histoire ?'
    )
})

fixture('O5_01_05 Recherche | Footer').beforeEach(async t => {
  await t.useRole(userRole).navigateTo(`${ROOT_PATH}recherche/`)
})

test("Lorsque je clique sur l'icône profil, la modale s'affiche", async t => {
  // when
  await t.click(menuButton).wait(100)

  // then
  await t
    .expect(mainMenu.visible)
    .ok()
    .expect(mainMenu.hasClass('entered'))
    .ok()
})
