import { Selector } from 'testcafe'
import { getVersoWallet, getVersoWalletValue } from './helpers/getVersoWallet'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

const openVersoButton = Selector('#deck-open-verso-button')

let userRole

fixture("04_01 Verso | L'utilisateur n'a pas d'argent").beforeEach(async t => {
  // given
  userRole = await createUserRoleFromUserSandbox(
    'webapp_04_verso',
    'get_existing_digital_offer_with_active_mediation_already_booked_and_user_hnmm_93'
  )
  await t.useRole(userRole)
})

test("L'utilisateur n'a plus d'argent sur son compte", async t => {
  await t.click(openVersoButton)

  const versoWallet = await getVersoWallet()
  const versoWalletValue = await getVersoWalletValue()
  await t
    .expect(versoWallet)
    .contains('€')
    .expect(versoWalletValue)
    .eql(0)
})
