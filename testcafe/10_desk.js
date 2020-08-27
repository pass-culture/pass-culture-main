import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { getPathname } from './helpers/location'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'

fixture('En étant sur la page de validation des contremarques,')

test('je peux valider une contremarque', async t => {
  const { booking, user } = await fetchSandbox(
    'pro_10_desk',
    'get_existing_pro_validated_user_with_validated_offerer_with_validated_user_offerer_with_thing_offer_with_stock_with_not_used_booking'
  )
  const pageTitleHeader = Selector('h1')
  const deskLink = Selector("a[href^='/guichet']")
  const navbarAnchor = Selector('a.navbar-link, span.navbar-burger').filterVisible()
  const codeInput = Selector('.form input[type="text"]')
  const state = Selector('.form .state')
  const stateText = Selector('.form .state span')
  const exitlink = Selector('#exitlink')
  const registerButton = Selector('.form button[type="submit"]')

  await t
    .useRole(createUserRole(user))
    .navigateTo(`${ROOT_PATH}guichet`)
    .click(navbarAnchor)
    .click(deskLink)
    .expect(pageTitleHeader.innerText)
    .eql('Guichet')
    .typeText(codeInput, booking.token)
    .expect(stateText.innerText)
    .eql('Coupon vérifié, cliquez sur "Valider" pour enregistrer')
    .expect(state.classNames)
    .contains('pending')
    .expect(codeInput.innerText)
    .eql('')
    .click(registerButton)
    .expect(state.classNames)
    .contains('success')
    .click(exitlink)
    .expect(getPathname())
    .eql('/accueil')
})
