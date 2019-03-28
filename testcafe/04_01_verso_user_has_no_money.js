// $(yarn bin)/testcafe chrome:headless ./testcafe/04_01_verso_user_has_no_money.js
import { Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { getVersoWallet, getVersoWalletValue } from './helpers/getVersoWallet'

const openVersoButton = Selector('#deck-open-verso-button')

fixture(`04_01 Verso`).beforeEach(async t => {
  // given
  const { user } = await fetchSandbox(
    'webapp_04_verso',
    'get_digital_offer_with_active_mediation_already_booked_and_user_hnmm_93'
  )
  await t.useRole(createUserRole(user))
})

test(`L'user n'a plus d'argent sur son compte`, async t => {
  await t.click(openVersoButton)

  const versoWallet = await getVersoWallet()
  const versoWalletValue = await getVersoWalletValue()
  await t
    .expect(versoWallet)
    .contains('€')
    .expect(versoWalletValue)
    .eql(0)
})
