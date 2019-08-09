import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { createUserRole } from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

const menuButton = Selector('#open-menu-button')

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

test('Menu | Liens | Aide', async t => {
  const expected = `https://docs.passculture.app/experimentateurs`
  const menuContact = Selector('.navlink').withText('Aide')
  await t.expect(menuContact.exists).ok()
  await t.expect(menuContact.getAttribute('href')).contains(expected)
})
