import { ClientFunction, Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { hasSignedUpUser93 } from './helpers/users'
import { ROOT_PATH, SUPPORT_EMAIL } from '../src/utils/config'

const menuButton = Selector('#open-menu-button')
const mainMenu = Selector('#main-menu')

fixture`12_01 Menu - Affichage de la modale`.beforeEach(async t => {
  await t
    .useRole(createUserRole(hasSignedUpUser93))
    .navigateTo(`${ROOT_PATH}profil`)
    .wait(500)
    .click(menuButton)
    .wait(100)
})

test("Lorsque je clique sur l'icône profil, la modale s'affiche", async t => {
  await t
    .expect(mainMenu.visible)
    .ok()
    .expect(mainMenu.hasClass('entered'))
    .ok()
})

test('Lorsque je clique sur la croix, la modale se referme', async t => {
  const closeButton = Selector('#main-menu-close-button')
  await t
    .wait(500)
    .click(closeButton)
    .wait(100)
  await t.expect(mainMenu.exists).notOk()
})

test('Je vois mon avatar dans le header', async t => {
  await t.expect(Selector('#main-menu-header-avatar').exists).ok()
})

test('Je vois le montant de mon pass dans le header', async t => {
  await t.expect(Selector('#main-menu-header-wallet-value').exists).ok()
})

fixture`12_02 Modale Menu - Liens vers pages`.beforeEach(async t => {
  await t
    .useRole(createUserRole(hasSignedUpUser93))
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
  const menuReservations = Selector('.navlink').withText('Mes Réservations')
  await t

    .expect(menuReservations.exists)
    .ok()
    .click(menuReservations)
    .wait(2100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/reservations')
})

test('Menu | Liens | Mes préférés', async t => {
  const menuFavoris = Selector('.navlink').withText('Mes Préférés')
  await t
    .expect(menuFavoris.exists)
    .ok()
    .expect(menuFavoris.hasAttribute('disabled'))
    .ok()
  // .click(menuFavoris)
  // .wait(100)
  // const location = await t.eval(() => window.location)
  // await t.expect(location.pathname).eql('/favoris')
})

test('Menu | Liens | Mon profil', async t => {
  const menuProfil = Selector('.navlink').withText('Mon Profil')
  await t
    .expect(menuProfil.exists)
    .ok()
    .click(menuProfil)
    .wait(100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/profil')
})

test('Menu | Liens | Nous contacter', async t => {
  const mailto = `mailto:${SUPPORT_EMAIL}`
  const menuContact = Selector('.navlink').withText('Nous contacter')
  await t.expect(menuContact.exists).ok()
  await t.expect(menuContact.getAttribute('href')).contains(mailto)
})

test('Menu | Liens | Mentions légales', async t => {
  const menuMentionsLegales = Selector('.navlink').withText('Mentions Légales')
  await t
    .expect(menuMentionsLegales.exists)
    .ok()
    .click(menuMentionsLegales)
    .wait(100)
  const location = await t.eval(() => window.location)
  await t
    .expect(location.href)
    .eql(
      'https://pass-culture.gitbook.io/documents/textes-normatifs/mentions-legales-et-conditions-generales-dutilisation-de-lapplication-pass-culture'
    )
})

test('Menu | Liens | Déconnexion', async t => {
  const menuLogoutButton = Selector('#main-menu-logout-button').withText(
    'Déconnexion'
  )

  await t
    .expect(menuLogoutButton.exists)
    .ok()
    .click(menuLogoutButton)
    .wait(500)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

fixture`12_03 Modale Menu - gestion de l'historique`.beforeEach(async t => {
  await t
    .useRole(createUserRole(hasSignedUpUser93))
    .navigateTo(`${ROOT_PATH}profil`)
    .wait(500)
    .click(menuButton)
    .wait(100)
})

test('Menu | Back button ferme le menu', async t => {
  // When
  const goBack = ClientFunction(() => window.history.back())
  await goBack()
  // Then
  await t.expect(mainMenu.exists).notOk()
})

test("Menu | Le menu ne reste pas dans l'historique de navigation", async t => {
  // given
  let location
  const goBack = ClientFunction(() => window.history.back())

  // when
  const menuProfil = Selector('.navlink').withText('Mon Profil')
  await t
    .expect(menuProfil.exists)
    .ok()
    .click(menuProfil)
    .wait(500)

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/profil')

  // when
  await goBack()
  await t.wait(500)

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/profil')
})
