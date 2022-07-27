import { Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'

fixture('En étant sur la page de validation des contremarques,')

test('je peux valider une contremarque', async t => {
  const { booking, user } = await fetchSandbox(
    'pro_10_desk',
    'get_existing_pro_validated_user_with_validated_offerer_with_validated_user_offerer_with_thing_offer_with_stock_with_not_used_booking'
  )

  const pageTitleHeader = Selector('h1')
  const deskLink = Selector('a').withText('Guichet')
  const codeInput = Selector('input[type="text"]')
  const deskMessage = Selector('div[data-testid="desk-message"]')
  const registerButton = Selector('button').withText('Valider la contremarque')

  await t
    .useRole(createUserRole(user))
    .click(deskLink)
    .expect(pageTitleHeader.innerText)
    .eql('Guichet')
    .typeText(codeInput, booking.token, { paste: true })
    .expect(deskMessage.innerText)
    .eql('Coupon vérifié, cliquez sur "Valider" pour enregistrer')
    .click(registerButton)
    .expect(deskMessage.innerText)
    .eql('Contremarque validée !')
})
