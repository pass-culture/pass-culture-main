import { Selector } from 'testcafe'

import {
  EXISTING_BOOKING_VALID_NOT_USED,
  BOOKING_BAD_CODE,
} from './helpers/bookings'
import { createUserRole } from './helpers/roles'
import { EXISTING_ADMIN_0_USER } from './helpers/users'
import { ROOT_PATH } from '../src/utils/config'

const pageTitleHeader = Selector('h1')
const deskLink = Selector("a[href^='/guichet']")
const navbarAnchor = Selector(
  'a.navbar-link, span.navbar-burger'
).filterVisible()
const codeInput = Selector('.form input[type="text"]')
const state = Selector('.form .state')
const stateText = Selector('.form .state span')
const exitlink = Selector('#exitlink')
const registerButton = Selector('.form button[type="submit"]')

fixture`DeskPage A | Saisir un code`.page`${ROOT_PATH}guichet`

test("L'état de départ de la page /guichet est conforme", async t => {
  await t.useRole(createUserRole(EXISTING_ADMIN_0_USER))
  // Navigation
  await t.click(navbarAnchor).click(deskLink)

  // intiial state
  await t.expect(pageTitleHeader.innerText).eql('Guichet')
  await t.expect(codeInput.innerText).eql('')
  await t.expect(stateText.innerText).eql('Saisissez un code')
  await t.expect(state.classNames).contains('pending')

  // typing...
  await t.typeText(codeInput, 'AZE')
  await t.expect(stateText.innerText).eql('caractères restants: 3/6')

  // Reset input
  t.selectText(codeInput).pressKey('delete')

  // typed + verified (beware of real validation lag)
  await t.typeText(codeInput, EXISTING_BOOKING_VALID_NOT_USED.token)
  await t
    .expect(stateText.innerText)
    .eql('Coupon vérifié, cliquez sur OK pour enregistrer')
  await t.expect(state.classNames).contains('pending')
  await t.expect(codeInput.innerText).eql('')

  // Reset input
  t.selectText(codeInput).pressKey('delete')

  // Bad input format
  await t.click(registerButton) // Rest field
  await t.typeText(codeInput, 'AZE{}')
  await t
    .expect(stateText.innerText)
    .eql('Caractères valides : de A à Z et de 0 à 9')
  await t.expect(state.classNames).contains('error')

  // Reset input
  t.selectText(codeInput).pressKey('delete')

  // Registration success
  await t.typeText(codeInput, EXISTING_BOOKING_VALID_NOT_USED.token)
  await t.click(registerButton)
  await t.expect(state.classNames).contains('success')

  // Registration failure
  await t.typeText(codeInput, BOOKING_BAD_CODE.token)
  await t.click(registerButton)
  await t.expect(state.classNames).contains('error')

  await t.click(exitlink)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/accueil')
})
