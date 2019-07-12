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

fixture('Desk A | Saisir un code').page(`${ROOT_PATH}guichet`)

test("L'état de départ de la page /guichet est conforme", async t => {
  // given
  const { booking, user } = await fetchSandbox(
    'pro_10_desk',
    'get_existing_pro_validated_user_with_validated_offerer_with_validated_user_offerer_with_thing_offer_with_stock_with_not_used_booking'
  )
  const { token } = booking
  await t.useRole(createUserRole(user))
  await t.click(navbarAnchor).click(deskLink)
  await t.expect(pageTitleHeader.innerText).eql('Guichet')
  await t.expect(codeInput.innerText).eql('')
  await t.expect(stateText.innerText).eql('Saisissez un code')
  await t.expect(state.classNames).contains('pending')

  await t.typeText(codeInput, 'AZE')
  await t.expect(stateText.innerText).eql('Caractères restants: 3/6')

  t.selectText(codeInput).pressKey('delete')

  await t.typeText(codeInput, token)
  await t.expect(stateText.innerText).eql('Coupon vérifié, cliquez sur "Valider" pour enregistrer')
  await t.expect(state.classNames).contains('pending')
  await t.expect(codeInput.innerText).eql('')

  t.selectText(codeInput).pressKey('delete')

  await t.click(registerButton)
  await t.typeText(codeInput, 'AZE{}')
  await t.expect(stateText.innerText).eql('Caractères valides : de A à Z et de 0 à 9')
  await t.expect(state.classNames).contains('error')

  t.selectText(codeInput).pressKey('delete')

  await t.typeText(codeInput, token)
  await t.click(registerButton)
  await t.expect(state.classNames).contains('success')

  await t.typeText(codeInput, 'ABC123')
  await t.click(registerButton)
  await t.expect(state.classNames).contains('error')

  await t.click(exitlink)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/accueil')
})
