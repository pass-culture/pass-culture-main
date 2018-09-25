import { Selector } from 'testcafe'
import { ROOT_PATH } from '../src/utils/config'
import { admin } from './helpers/roles'

const subTitleHeader = Selector('h2')
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

const TEST_GOOD_CODE = '2ALYY5'
const TEST_BAD_CODE = 'ABC123'

fixture`08_01 Guichet | Page guichet`.page`${ROOT_PATH}guichet`

test("L'état de départ de la page /guichet est conforme", async t => {
  await t.useRole(admin)
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
  await t.typeText(codeInput, TEST_GOOD_CODE)
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
  await t.typeText(codeInput, TEST_GOOD_CODE)
  await t.click(registerButton)
  await t.expect(state.classNames).contains('success')

  // Registration failure
  await t.typeText(codeInput, TEST_BAD_CODE)
  await t.click(registerButton)
  await t.expect(state.classNames).contains('error')

  await t.click(exitlink).wait(500)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/accueil')
})
