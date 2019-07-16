import { Selector } from 'testcafe'

import { navigateToReimbursementsAs } from './helpers/navigations'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

fixture('Reimbursements A | Je peux télécharger un csv de mes remboursements').page(
  `${ROOT_PATH + 'connexion'}`
)

test('Je clique sur le bouton télécharger', async t => {
  // given
  const downloadButton = Selector('button[download]')
  const { user } = await fetchSandbox(
    'pro_13_reimbursements',
    'get_existing_pro_validated_user_with_validated_offerer_with_reimbursement'
  )
  await navigateToReimbursementsAs(user)(t)

  // when
  await t.click(downloadButton)
})
