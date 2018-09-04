import { Selector } from 'testcafe'
import { ROOT_PATH } from '../src/utils/config'
import { regularOfferer } from './helpers/roles'

const subTitleHeader = Selector('h2')
const pageTitleHeader = Selector('h1')
const counterLink = Selector("a[href^='/guichet']")
const navbarAnchor = Selector(
  'a.navbar-link, span.navbar-burger'
).filterVisible()
const codeInput = Selector('.form input[type="text"]')
const state = Selector('.form .state')
const resetButton = Selector('.form input[type="reset"]')
const registerButton = Selector('.form button[type="submit"]')

// @TODO Get a working code
const TEST_GOOD_CODE = 'ABC123'
// @TODO Get a not working code
const TEST_BAD_CODE = 'ABC123'

fixture`08_01 Guichet | Page guichet`.page`${ROOT_PATH}guichet`

test("L'état de départ de la page /guichet est conforme", async t => {
  await t.useRole(regularOfferer)
  // Navigation
  await t.click(navbarAnchor).click(counterLink)

  // intiial state
  await t.expect(pageTitleHeader.innerText).eql('Guichet')
  await t.expect(codeInput.innerText).eql('')
  await t.expect(Selector('.form .state').innerText).eql('Saisissez un code')
  await t.expect(state.classNames).contains('success')

  // typing...
  await t.typeText(codeInput, 'AZE')
  await t.expect(state.innerText).eql('caractères restants: 3/6')

  // typed + verified (beware of real validation lag)
  await t.typeText(codeInput, TEST_GOOD_CODE)
  await t
    .expect(state.innerText)
    .eql('Booking vérifié, cliquez sur OK pour enregistrer')
  await t.expect(state.classNames).contains('success')

  // reset
  await t.click(resetButton)
  await t.expect(codeInput.innerText).eql('')
  await t.expect(state.innerText).eql('Saisissez un code')
  await t.expect(state.classNames).contains('success')

  // Bad input format
  await t.typeText(codeInput, 'AZE{}')
  await t
    .expect(state.innerText)
    .eql('Caractères valides : de A à Z et de 0 à 9')
  await t.expect(state.classNames).contains('error')

  // @TODO : Complete with adequate codes
  // // Registration success
  // await t.click(resetButton)
  // await t.typeText(codeInput, TEST_GOOD_CODE)
  // await t.click(registerButton)
  // await t.expect(state.classNames).contains('success')
  //
  // // Registration failure
  // await t.click(resetButton)
  // await t.typeText(codeInput, TEST_BAD_CODE)
  // await t.click(registerButton)
  // await t.expect(state.classNames).contains('error')
})
