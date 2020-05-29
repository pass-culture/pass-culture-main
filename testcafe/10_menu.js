import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { createUserRole } from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

fixture('En navigant sur la navbar').beforeEach(async t => {
  const { user } = await fetchSandbox(
    'webapp_10_menu',
    'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
  )
  await t.useRole(createUserRole(user)).navigateTo(`${ROOT_PATH}profil`)
})

test('je peux naviguer vers mes offres', async t => {
  const navBarOfferLink = Selector('nav ul li a').nth(0)
  await t
    .expect(navBarOfferLink.exists)
    .ok()
    .click(navBarOfferLink)
    .wait(100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).contains('decouverte')
})

test('je peux naviguer vers la recherche', async t => {
  const navBarSearchLink = Selector('nav ul li a').nth(1)
  await t
    .expect(navBarSearchLink.exists)
    .ok()
    .click(navBarSearchLink)
    .wait(100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).contains('recherche')
})

test('je peux naviguer vers mes réservations', async t => {
  const navBarBookingsLink = Selector('nav ul li a').nth(2)
  await t
    .expect(navBarBookingsLink.exists)
    .ok()
    .click(navBarBookingsLink)
    .wait(2100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/reservations')
})

test('je peux naviguer vers les favoris', async t => {
  const navBarFavoritesLink = Selector('nav ul li a').nth(3)
  await t
    .expect(navBarFavoritesLink.exists)
    .ok()
    .click(navBarFavoritesLink)
    .wait(2100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/favoris')
})

test('je peux naviguer vers mon profil', async t => {
  const navBarProfileLink = Selector('nav ul li a').nth(4)
  await t
    .expect(navBarProfileLink.exists)
    .ok()
    .click(navBarProfileLink)
    .wait(100)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).contains('profil')
})
