import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import getPageUrl from './helpers/getPageUrl'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'

const navBar = Selector('nav ul li a')

fixture('En navigant sur la navbar').beforeEach(async t => {
  const { user } = await fetchSandbox(
    'webapp_10_menu',
    'get_existing_webapp_validated_user_with_has_filled_cultural_survey',
  )
  await t.useRole(createUserRole(user)).navigateTo(`${ROOT_PATH}profil`)
})

test('je peux naviguer vers mes offres', async t => {
  const navBarOfferLink = navBar.nth(0)
  await t
    .expect(navBarOfferLink.exists)
    .ok()
    .click(navBarOfferLink)
    .expect(getPageUrl())
    .contains(`${ROOT_PATH}decouverte/`)
})

test('je peux naviguer vers la recherche', async t => {
  const navBarSearchLink = navBar.nth(1)
  await t
    .expect(navBarSearchLink.exists)
    .ok()
    .click(navBarSearchLink)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}recherche`)
})

test('je peux naviguer vers la page accueil', async t => {
  const navBarSearchLink = navBar.nth(2)
  await t
    .expect(navBarSearchLink.exists)
    .ok()
    .click(navBarSearchLink)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}accueil`)
})

test('je peux naviguer vers mes réservations', async t => {
  const navBarBookingsLink = navBar.nth(3)
  await t
    .expect(navBarBookingsLink.exists)
    .ok()
    .click(navBarBookingsLink)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}reservations`)
})

test('je peux naviguer vers les favoris', async t => {
  const navBarFavoritesLink = navBar.nth(4)
  await t
    .expect(navBarFavoritesLink.exists)
    .ok()
    .click(navBarFavoritesLink)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}favoris`)
})
