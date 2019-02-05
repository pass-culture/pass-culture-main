import { Selector, ClientFunction } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'

import { createUserRole, signinAs } from './helpers/roles'
import { hasBookedSomeUser93, hasSignedUpUser93 } from './helpers/users'

const getPageUrl = ClientFunction(() => window.location.href.toString())

const nextButton = Selector('button.button.after')
const showVerso = Selector('button.button.to-recto')
const versoDiv = Selector('div.verso')
const clueDiv = Selector('div.clue')
const closeButton = Selector('.close-button')

// WEIRD: PROFILE BUTTON EVEN IF IT IS VISIBLE
// IS NOT CLICKABLE
// const profileButton = Selector('button.profile-button')
// WE NEED TO PASS BY MENTION LEGAL PAGE
// IN ORDER TO NAVIGATE TO SIGNOUT
const menuButton = Selector('#open-menu-button')
const menuLogoutButton = Selector('#main-menu-logout-button')

fixture('O3_01 Découverte | Je ne suis pas connecté·e').page(
  `${ROOT_PATH}decouverte`
)

test('Je suis redirigé vers la page /connexion', async t => {
  await t.expect(getPageUrl()).contains('/connexion', { timeout: 10000 })
})

fixture('O3_02 Découverte | A la première connexion')

test('Je fais ma première visite sur découverte', async t => {
  await t.navigateTo(`${ROOT_PATH}connexion`)
  await signinAs(hasSignedUpUser93)(t)

  await t
    .wait(500)
    .expect(Selector('#application-loader').innerText)
    .match(/Chargement des offres/)

  await t
    .wait(5000)
    .expect(getPageUrl())
    .contains('/decouverte/tuto/', { timeout: 1000 })

  await t
    .click(nextButton)
    .wait(1000)
    .expect(getPageUrl())
    .contains('/decouverte/tuto/', { timeout: 1000 })

  await t
    .expect(clueDiv.visible)
    .ok()
    .click(showVerso)
    .wait(1000)
    .expect(versoDiv.hasClass('flipped'))
    .ok()
    .click(closeButton)
    .expect(versoDiv.hasClass('flipped'))
    .notOk()
    .wait(1000)

  await t.click(nextButton).wait(1000)

  // to emulate a disconnection, signout et re signin
  await t
    .navigateTo(`${ROOT_PATH}profil`)
    .wait(500)
    .click(menuButton)
    .wait(100)
    .click(menuLogoutButton)
  await signinAs(hasSignedUpUser93)(t)
  // or do a hard refresh
  // await t.eval(() => window.location.reload(true))

  await t
    .wait(5000)
    .expect(getPageUrl())
    .notContains('/decouverte/tuto/', { timeout: 1000 })
})

fixture('O3_02 Découverte | exploration | Recommendations').beforeEach(
  async t => {
    await t.useRole(createUserRole(hasBookedSomeUser93))
  }
)

test('Je ne vois plus les cartes tutos', async t => {
  await t
    .wait(2000)
    .expect(getPageUrl())
    .notContains('/decouverte/tuto/', { timeout: 1000 })
})

test.skip("Je vois les informations de l'accroche du recto", async t => {
  await t
  // TODO
})

test.skip('Je vois le verso des cartes lorsque je fais glisser la carte vers le haut', async t => {
  await t.click(showVerso).wait(1000)
  await t.expect(versoDiv.find('h1').innerText).eql('Vhils')
  await t.expect(versoDiv.find('h2').innerText).eql('LE CENTQUATRE-PARIS')
  // TODO
})

// TODO tester le drag des images https://devexpress.github.io/testcafe/documentation/test-api/actions/drag-element.html

// S'il n'y a pas d'offres, je vois le message 'Aucune offre pour le moment' et je peux accéder au menu profil
