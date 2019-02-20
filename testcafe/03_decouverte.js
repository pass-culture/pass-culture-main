import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import getPageUrl from './helpers/getPageUrl'
import { createUserRole, signinAs } from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

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

fixture('O3_01 Découverte | Je ne suis pas connecté·e')

test('Je suis redirigé vers la page /connexion', async t => {
  // when
  await t.navigateTo(`${ROOT_PATH}decouverte`)

  // then
  await t.expect(getPageUrl()).contains('/connexion', { timeout: 10000 })
})

fixture('O3_02 Découverte | A la première connexion')

test('Je fais ma première visite sur découverte', async t => {
  // given
  const { user } = await fetchSandbox(
    'webapp_03_decouverte',
    'get_existing_webapp_user_with_no_date_read'
  )

  // when
  await t.useRole(createUserRole(user))

  // then
  await t
    .wait(500)
    .expect(Selector('#application-loader').innerText)
    .match(/Chargement des offres/)
    .wait(5000)
    .expect(getPageUrl())
    .contains('/decouverte/tuto/', { timeout: 1000 })

  // when
  await t.click(nextButton).wait(1000)

  // then
  await t.expect(getPageUrl()).contains('/decouverte/tuto/', { timeout: 1000 })
  await t.expect(clueDiv.visible).ok()

  // when
  await t.click(showVerso).wait(1000)
  // then
  await t.expect(versoDiv.hasClass('flipped')).ok()

  // when
  await t.click(closeButton)

  // then
  await t
    .expect(versoDiv.hasClass('flipped'))
    .notOk()
    .wait(1000)

  // when
  await t.click(nextButton).wait(1000)
  // to emulate a disconnection, signout et re signin
  await t
    .navigateTo(`${ROOT_PATH}profil`)
    .wait(500)
    .click(menuButton)
    .wait(100)
    .click(menuLogoutButton)
  await signinAs(user)(t)
  // or do a hard refresh
  // await t.eval(() => window.location.reload(true))

  // then
  await t
    .wait(5000)
    .expect(getPageUrl())
    .notContains('/decouverte/tuto/', { timeout: 1000 })
})

fixture('O3_02 Découverte | exploration | Recommendations').beforeEach(
  async t => {
    const { user } = await fetchSandbox(
      'webapp_03_decouverte',
      'get_existing_webapp_user_with_bookings'
    )
    return t.useRole(createUserRole(user))
  }
)

test('Je ne vois plus les cartes tutos', async t => {
  // then
  await t
    .wait(2000)
    .expect(getPageUrl())
    .notContains('/decouverte/tuto/', { timeout: 1000 })
})

test.skip("*TODO* Je vois les informations de l'accroche du recto", async t => {
  await t
  // TODO
})

test.skip('*TODO* Je vois le verso des cartes lorsque je fais glisser la carte vers le haut', async t => {
  await t.click(showVerso).wait(1000)
  await t.expect(versoDiv.find('h1').innerText).eql('Vhils')
  await t.expect(versoDiv.find('h2').innerText).eql('LE CENTQUATRE-PARIS')
  // TODO
})

// TODO tester le drag des images https://devexpress.github.io/testcafe/documentation/test-api/actions/drag-element.html

// S'il n'y a pas d'offres, je vois le message 'Aucune offre pour le moment' et je peux accéder au menu profil
