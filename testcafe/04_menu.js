import { Selector } from 'testcafe'

import regularUser from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

const menuButton = Selector('#open-menu-button')
const mainMenu = Selector('#main-menu')

fixture`04_01 Menu - Affichage de la modale`.beforeEach(async t => {
  await t
    .useRole(regularUser)
    .navigateTo(`${ROOT_PATH}mentions-legales/`)
    .wait(500)
    .click(menuButton)
    .wait(500)
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
    .wait(500)
  await t.expect(mainMenu.hasClass('exited')).ok()
})

test('Je vois mon avatar dans le header', async t => {
  await t.expect(Selector('#main-menu-header-avatar')).ok()
})

test('Je vois le montant de mon pass dans le header', async t => {
  await t.expect(Selector('#main-menu-header-wallet-value')).ok()
})

fixture`04_02 Modale Menu - Liens vers pages`.beforeEach(async t => {
  await t
    .useRole(regularUser)
    .navigateTo(`${ROOT_PATH}mentions-legales/`)
    .wait(500)
    .click(menuButton)
    .wait(500)
})

test('Menu | Liens | Les offres', async t => {
  const menuOffres = Selector('.navlink').withText('Les offres')
  await t

    .expect(menuOffres)
    .ok()
    .click(menuOffres)
    .wait(200)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).contains('decouverte')
})

test('Menu | Liens | Recherche', async t => {
  const menuRecherche = Selector('.navlink').withText('Recherche')
  await t

    .expect(menuRecherche)
    .ok()
    .expect(menuRecherche.hasAttribute('disabled'))
    .ok()
  // .click(menuRecherche)
  // .wait(200)
  // const location = await t.eval(() => window.location)
  // await t.expect(location.pathname).eql('/recherche')
})

test('Menu | Liens | Mes réservations', async t => {
  const menuReservartions = Selector('.navlink').withText('Mes Réservations')
  await t

    .expect(menuReservartions)
    .ok()
    .click(menuReservartions)
    .wait(200)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/reservations')
})

test('Menu | Liens | Mes préférés', async t => {
  const menuFavoris = Selector('.navlink').withText('Mes Préférés')

  await t
    .expect(menuFavoris)
    .ok()
    .expect(menuFavoris.hasAttribute('disabled'))
    .ok()
  // .click(menuFavoris)
  // .wait(200)
  // const location = await t.eval(() => window.location)
  // await t.expect(location.pathname).eql('/favoris')
})

test('Menu | Liens | Mon profil', async t => {
  const menuProfil = Selector('.navlink').withText('Mon Profil')
  await t

    .expect(menuProfil)
    .ok()
    .click(menuProfil)
    .wait(200)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/profil')
})

test('Menu | Liens | Nous contacter', async t => {
  const menuContact = Selector('.navlink').withText('Nous contacter')
  await t.expect(menuContact).ok()
})

test('Menu | Liens | Mentions légales', async t => {
  const menuMentionsLegales = Selector('.navlink').withText('Mentions Légales')
  await t

    .expect(menuMentionsLegales)
    .ok()
    .click(menuMentionsLegales)
    .wait(200)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/mentions-legales/')
})

test('Menu | Liens | Déconnexion', async t => {
  const menuDeconnexion = Selector('#main-menu-logout-button').withText(
    'Déconnexion'
  )

  await t
    .expect(menuDeconnexion)
    .ok()
    .click(menuDeconnexion)
    .wait(1000)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})
