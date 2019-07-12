import { ClientFunction, Selector } from 'testcafe'
import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

const loaderScreen = Selector('#application-loader')
const currentCard = Selector('div.card.current')
const nextButton = Selector('button.button.after')
const previousButton = Selector('button.button.before')
const showVerso = Selector('button.button.to-recto')
const versoDiv = Selector('div.verso')
const closeVersoLink = Selector('#deck .close-link')
const menuButton = Selector('#open-menu-button')
const menuLogoutButton = Selector('#main-menu-logout-button')

const getNbRecos = ClientFunction(() => document.querySelector('#deck').dataset.nbRecos)

let userRole1
let userRole2

fixture('O3_01 Découverte | Je ne suis pas connecté·e')

test('Je suis redirigé vers la page /connexion', async t => {
  // when
  await t.navigateTo(`${ROOT_PATH}decouverte`)

  // then
  await t.expect(getPageUrl()).contains('/connexion', { timeout: 10000 })
})

fixture('O3_02 Découverte | A la première connexion').beforeEach(async t => {
  if (!userRole1) {
    userRole1 = await createUserRoleFromUserSandbox(
      'webapp_03_decouverte',
      'get_existing_webapp_user_with_no_date_read'
    )
  }
  await t.useRole(userRole1)
})

test('Je fais ma première visite sur découverte', async t => {
  await t.expect(getPageUrl()).contains('/decouverte/tuto/')

  await t
    .click(nextButton)
    .expect(getPageUrl())
    .contains('/decouverte/tuto/')

  await t.expect(versoDiv.hasClass('flipped')).notOk()

  await t.click(nextButton)

  await t
    .navigateTo(`${ROOT_PATH}profil`)
    .click(menuButton)
    .click(menuLogoutButton)

  await t.expect(getPageUrl()).notContains('/decouverte/tuto/')
})

fixture('O3_03 Découverte | exploration | Recommendations').beforeEach(async t => {
  if (!userRole2) {
    userRole2 = await createUserRoleFromUserSandbox(
      'webapp_03_decouverte',
      'get_existing_webapp_user_with_bookings'
    )
  }
  await t.useRole(userRole2)
})

test('Je ne vois plus les cartes tutos', async t => {
  // then
  await t.expect(getPageUrl()).contains('/decouverte/')
  await t.expect(getPageUrl()).notContains('/decouverte/tuto/')
})

test('Je peux passer de carte en carte en glissant les cartes vers les cotés', async t => {
  await t.navigateTo(`${ROOT_PATH}decouverte`)
  await t.expect(nextButton.visible).ok()

  const urlAtStart = getPageUrl()
  await t.drag(currentCard, -100, 0)
  await t.expect(getPageUrl()).notEql(urlAtStart)
  await t.expect(previousButton.visible).ok()

  await t.drag(currentCard, 100, 0)
  await t.expect(getPageUrl()).notEql(urlAtStart)
})

test('Je peux afficher le verso des cartes en cliquant sur le bouton "haut"', async t => {
  await t.click(showVerso)
  await t.expect(versoDiv.hasClass('flipped')).ok()
  await t.click(closeVersoLink)
  await t.expect(versoDiv.hasClass('flipped')).notOk()
})

test('Je peux afficher/cacher le verso des cartes en glissant vers le haut/bas', async t => {
  await t.drag(currentCard, 0, -100)
  await t.expect(versoDiv.hasClass('flipped')).ok()

  await t.drag(currentCard, 0, 100)
  await t.expect(versoDiv.hasClass('flipped')).notOk()
})

test("Je vois l'écran de chargement si je passe de carte en carte très vite vers la droite, mais pas si je reviens vers la gauche", async t => {
  await t.navigateTo(`${ROOT_PATH}decouverte`)
  await t.expect(loaderScreen.visible).ok({ timeout: 10000 })
  await t.click(nextButton)
  const nbRecos = getNbRecos()
  let urlAfter
  let urlBefore
  for (let count = 0; count <= nbRecos + 1; count += 1) {
    urlBefore = getPageUrl()
    await t.click(nextButton)
    await t.expect(getPageUrl()).notEql(urlBefore)
    urlAfter = await getPageUrl()

    if (urlAfter.endsWith('/decouverte/tuto/fin')) {
      await t.expect(loaderScreen.visible).ok({ timeout: 10000 })
      break
    }
  }

  urlBefore = getPageUrl()
  await t.click(previousButton, { timeout: 10000 })
  await t.expect(getPageUrl()).notEql(urlBefore)

  urlBefore = getPageUrl()
  await t.click(nextButton)
  await t.expect(getPageUrl()).notEql(urlBefore)
  await t.expect(getPageUrl()).notEql('/decouverte/tuto/fin')
})

test("Je vois la carte finale si j'arrive à la fin des cartes", async t => {
  await t.navigateTo(`${ROOT_PATH}decouverte`).click(nextButton)
  let seenFinalCard = false
  let x
  let urlAfter
  let urlBefore
  for (x = 0; x <= 200; x += 1) {
    urlBefore = getPageUrl()
    await t.click(nextButton)
    await t.expect(getPageUrl()).notEql(urlBefore)
    urlAfter = await getPageUrl()
    if (urlAfter.endsWith('/decouverte/tuto/fin')) {
      await t
        .expect(loaderScreen.visible)
        .notOk({ timeout: 10000 })
        .wait(2000) // Utilisation exceptionnelle de wait, car il y a plusieurs cas possibles (redirection ou alors on tombe sur 'parcouru toutes les offres')
    }
    urlAfter = await getPageUrl()
    if (urlAfter.endsWith('/decouverte/tuto/fin')) {
      await t
        .expect(Selector('div.card.current > div.recto', { visibilityCheck: true }).textContent)
        .match(/parcouru toutes les offres/)
      seenFinalCard = true
      break
    }
  }
  await t.expect(seenFinalCard).ok("La carte finale s'affiche")
})
