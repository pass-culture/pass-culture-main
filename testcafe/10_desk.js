import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { createUserRole } from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

const pageTitleHeader = Selector('h1')
const deskLink = Selector("a[href^='/guichet']")
const navbarAnchor = Selector('a.navbar-link, span.navbar-burger').filterVisible()
const codeInput = Selector('.form input[type="text"]')
const state = Selector('.form .state')
const stateText = Selector('.form .state span')
const exitlink = Selector('#exitlink')
const registerButton = Selector('.form button[type="submit"]')

fixture('En étant sur la page de validation des contremarques').page(`${ROOT_PATH}guichet`)

test('Je peux valider une contremarque', async t => {
  // given
  const { booking, user } = await fetchSandbox(
    'pro_10_desk',
    'get_existing_pro_validated_user_with_validated_offerer_with_validated_user_offerer_with_thing_offer_with_stock_with_not_used_booking'
  )
  const { token } = booking
  await t.useRole(createUserRole(user))
  await t.click(navbarAnchor).click(deskLink)
  await t.expect(pageTitleHeader.innerText).eql('Guichet')

  // when
  await t
    .typeText(codeInput, token)
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

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/accueil')
})
