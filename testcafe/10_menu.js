import { ClientFunction, Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { createUserRole } from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

const menuButton = Selector('#open-menu-button')
const mainMenu = Selector('#main-menu')

let userRole
fixture('10_01 Menu - Affichage de la modal').beforeEach(async t => {
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_10_menu',
      'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
    )
  }
  await t
    .useRole(userRole)
    .navigateTo(`${ROOT_PATH}profil`)
    .wait(500)
    .click(menuButton)
    .wait(100)
})

test("Lorsque je clique sur l'icône compte, la modal s'affiche", async t => {
  await t
    .expect(mainMenu.visible)
    .ok()
    .expect(mainMenu.hasClass('entered'))
    .ok()
})

test('Lorsque je clique sur la croix, la modal se referme', async t => {
  const closeMenu = Selector('#main-menu-fixed-container .close-link')
  await t
    .wait(500)
    .click(closeMenu)
    .wait(100)
  await t.expect(mainMenu.exists).notOk()
})

test('Je vois mon avatar dans le header', async t => {
  await t.expect(Selector('#main-menu-header-avatar').exists).ok()
})

test('Je vois le montant de mon pass dans le header', async t => {
  await t.expect(Selector('#main-menu-header-wallet-value').exists).ok()
})

fixture('10_02 - Modal Menu - Liens vers pages').beforeEach(async t => {
  const { user } = await fetchSandbox(
    'webapp_10_menu',
    'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
  )
  await t
    .useRole(createUserRole(user))
    .navigateTo(`${ROOT_PATH}profil`)
    .wait(500)
    .click(menuButton)
    .wait(100)
})

test('Menu | Liens | Les offres', async t => {
  const menuOffres = Selector('.navlink').withText('Les offres')
  await t

    .expect(menuOffres.exists)
    .ok()
    .click(menuOffres)
    .wait(100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).contains('decouverte')
})

test('Menu | Liens | Recherche', async t => {
  const menuRecherche = Selector('.navlink').withText('Recherche')
  await t
    .expect(menuRecherche.exists)
    .ok()
    .click(menuRecherche)
    .wait(100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/recherche')
})

test('Menu | Liens | Mes réservations', async t => {
  const menuReservations = Selector('.navlink').withText('Mes réservations')
  await t
    .expect(menuReservations.exists)
    .ok()
    .click(menuReservations)
    .wait(2100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/reservations')
})

test('Menu | Liens | Mes favoris', async t => {
  const menuFavoris = Selector('.navlink').withText('Mes favoris')
  await t
    .expect(menuFavoris.exists)
    .ok()
    .click(menuFavoris)
    .wait(2100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/favoris')
})

test('Menu | Liens | Mon compte', async t => {
  const menuCompte = Selector('.navlink').withText('Mon compte')
  await t
    .expect(menuCompte.exists)
    .ok()
    .click(menuCompte)
    .wait(100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/profil')
})

test('Menu | Liens | Aide', async t => {
  const expected = `https://docs.passculture.app/experimentateurs`
  const menuContact = Selector('.navlink').withText('Aide')
  await t.expect(menuContact.exists).ok()
  await t.expect(menuContact.getAttribute('href')).contains(expected)
})

test('Menu | Liens | Mentions légales', async t => {
  const menuMentionsLegales = Selector('.navlink').withText('Mentions légales')
  await t.expect(menuMentionsLegales.exists).ok()
  await t
    .expect(menuMentionsLegales.getAttribute('href'))
    .eql(
      'https://pass-culture.gitbook.io/documents/textes-normatifs/mentions-legales-et-conditions-generales-dutilisation-de-lapplication-pass-culture'
    )
})

test('Menu | Liens | Déconnexion', async t => {
  const menuLogoutButton = Selector('#main-menu-logout-button').withText('Déconnexion')

  await t
    .expect(menuLogoutButton.exists)
    .ok()
    .click(menuLogoutButton)
    .wait(500)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

fixture("10_03 - Modal Menu - gestion de l'historique").beforeEach(async t => {
  await t
    .useRole(userRole)
    .navigateTo(`${ROOT_PATH}profil`)
    .wait(500)
    .click(menuButton)
    .wait(100)
})

test('Menu | Back button ferme le menu', async t => {
  // when
  const goBack = ClientFunction(() => window.history.back())
  await goBack()
  // then
  await t.expect(mainMenu.exists).notOk()
})

test("Menu | Le menu ne reste pas dans l'historique de navigation", async t => {
  // given
  let location
  const goBack = ClientFunction(() => window.history.back())

  // when
  const menuCompte = Selector('.navlink').withText('Mon compte')
  await t
    .expect(menuCompte.exists)
    .ok()
    .click(menuCompte)
    .wait(500)

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/profil')

  // when
  await goBack()
  await t.wait(500)

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/profil/menu')
})
