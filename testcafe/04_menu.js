import { Selector } from 'testcafe'

import regularUser from './helpers/roles'

const footer = Selector('.footer').filterVisible()
const rectoDivProfileButton = footer.find('button.profile-button')
const mainMenu = Selector('.main-menu')
// const profilePic = Selector('.modal').find('profile-pic')
const closeButton = Selector('.close')
const menuList = Selector('div.menu ul li a')
// const header = Selector('header')
const offres = menuList.nth(0)
const reservations = menuList.nth(1)
const favoris = menuList.nth(2)
const profil = menuList.nth(4)
const mentions = menuList.nth(5)
const contact = menuList.nth(6)
const deconnexion = menuList.nth(7)

// const menuButton = Selector('.profile-button')

const profilLink = Selector('.navlink').withText('Mon Profil')

fixture.skip`04_01 Modale Menu`.beforeEach(async t => {
  await t.useRole(regularUser)
})

test("Lorsque je clique sur l'icône menu, la modale s'affiche", async t => {
  await t
    // .useRole(regularUser)
    // .click(menuButton)
    .expect(mainMenu.visible)

  // .wait(500)
  // .expect(mainMenu.count).eql(1)
})

test("Lorsque je clique sur l'icône profil, la modale s'affiche", async t => {
  await t.click(rectoDivProfileButton.nth(1))
  await t
    .expect(mainMenu.visible)
    .expect(mainMenu.count)
    .toEq(1)
    .ok()
    .expect(mainMenu.hasClass('active'))
    .ok()

    // Header

    // Close Modal
    .click(closeButton)
    .wait(200)
  await t
    .expect(mainMenu.visible)
    .notOk()
    .expect(mainMenu.hasClass('active'))
    .notOk()
})

test.skip('Menu | Les offres', async t => {
  await t
    .click(rectoDivProfileButton.nth(1))

    .expect(offres.innerText)
    .eql('Les offres')
    .click(offres)
    .wait(200)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).contains('decouverte')
})

test.skip('Menu | Mes réservations', async t => {
  await t
    .click(rectoDivProfileButton.nth(1))

    .expect(reservations.innerText)
    .eql('Mes réservations')
    .click(reservations)
    .wait(200)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/reservations')
})

test.skip('Menu | Mes préférés', async t => {
  await t
    .click(rectoDivProfileButton.nth(1))

    .expect(favoris.innerText)
    .eql('Mes préférés')
    .click(favoris)
    .wait(200)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/favoris')
})

test('Menu | Mon profil', async t => {
  await t
    .expect(profilLink.count)
    .eql(1)
    .expect(profilLink.innerText)
    .eql('\nMon Profil\n')
    .expect(profil.hasAttribute('disabled'))
    .ok()

  // .click(profilLink)
  // .wait(200)
  // const location = await t.eval(() => window.location)
  // await t.expect(location.pathname).eql('/profil')
})

test.skip('Menu | Mentions légales', async t => {
  await t
    .click(rectoDivProfileButton.nth(1))

    .expect(mentions.innerText)
    .eql('Mentions légales')
    .click(mentions)
    .wait(200)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/mentions-legales')
})

test.skip('Menu | Nous contacter', async t => {
  await t
    .click(rectoDivProfileButton.nth(1))
    .expect(contact.innerText)
    .eql('Nous contacter')
})

test.skip('Menu | Déconnexion', async t => {
  await t
    .click(rectoDivProfileButton.nth(1))

    .expect(deconnexion.innerText)
    .eql('Déconnexion')
    .click(deconnexion)
    .wait(1000)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test.skip('Menu | Recherche', async t => {
  await t
    .click(rectoDivProfileButton.nth(1))

    .expect(deconnexion.innerText)
    .eql('Recherche')
    .click(deconnexion)
    .wait(1000)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/recherche')
})
