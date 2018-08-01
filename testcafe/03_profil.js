import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import regularUser from './helpers/roles'

const footer = Selector('.footer').filterVisible()
const rectoDivProfileButton = footer.find('button.profile-button')
const profileModal = Selector('.modal')
const profilePic = Selector('.modal').find('profile-pic')
const closeButton = Selector('.close')
const menuList = Selector('div.menu ul li a')
const header = Selector('header')
const offres = menuList.nth(0)
const reservations = menuList.nth(1)
const favoris = menuList.nth(2)
const reglages = menuList.nth(3)
const profil = menuList.nth(4)
const mentions = menuList.nth(5)
const contact = menuList.nth(6)
const deconnexion = menuList.nth(7)

fixture `03_01 Modale Profil`
    .beforeEach( async t => {
      await t
      .useRole(regularUser)
      .navigateTo(ROOT_PATH+'decouverte/AH7Q/AU')
   })

  test("Lorsque je clique sur l'icône profil, la modale s'affiche", async t => {

      await t
      .click(rectoDivProfileButton.nth(1))
      await t.expect(profileModal.visible).ok()
      .expect(profileModal.hasClass('active')).ok()

      // Header

      // Close Modal
      .click(closeButton)
      .wait(200)
      await t.expect(profileModal.visible).notOk()
      .expect(profileModal.hasClass('active')).notOk()

  })

  test("Menu | Les offres", async t => {

    await t
    .click(rectoDivProfileButton.nth(1))

    .expect(offres.innerText).eql('Les offres')
    .click(offres)
    .wait(200)
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).contains('decouverte')
  })

  test("Menu | Mes réservations", async t => {

    await t
    .click(rectoDivProfileButton.nth(1))

    .expect(reservations.innerText).eql('Mes réservations')
    .click(reservations)
    .wait(200)
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/reservations')
  })

  test("Menu | Mes préférés", async t => {

    await t
    .click(rectoDivProfileButton.nth(1))

    .expect(favoris.innerText).eql('Mes préférés')
    .click(favoris)
    .wait(200)
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/favoris')
  })

  test("Menu | Réglages", async t => {

    await t
    .click(rectoDivProfileButton.nth(1))

    .expect(reglages.innerText).eql('Réglages')
    .expect(reglages.hasAttribute('disabled')).ok()
  })

  test("Menu | Mon profil", async t => {

    await t
    .click(rectoDivProfileButton.nth(1))

    .expect(profil.innerText).eql('Mon profil')
    .expect(profil.hasAttribute('disabled')).ok()
  })

  test("Menu | Mentions légales", async t => {

    await t
    .click(rectoDivProfileButton.nth(1))

    .expect(mentions.innerText).eql('Mentions légales')
    .click(mentions)
    .wait(200)
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/mentions-legales')
  })

  test("Menu | Nous contacter", async t => {

    await t
    .click(rectoDivProfileButton.nth(1))
    .expect(contact.innerText).eql('Nous contacter')

  })

  test("Menu | Déconnexion", async t => {

    await t
    .click(rectoDivProfileButton.nth(1))

    .expect(deconnexion.innerText).eql('Déconnexion')
    .click(deconnexion)
    .wait(1000)
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/connexion')
  })
