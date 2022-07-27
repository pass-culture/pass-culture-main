import { Selector } from 'testcafe'

import { getPathname } from './helpers/location'
import { navigateToHomeAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'

fixture(
  'Lorsque je clique sur le menu, je clique sur le lien pour atteindre mes "structures",'
)

test('si j’ai une structure validée, je clique sur celle-ci afin d’accéder au détail', async t => {
  const { user, offerer } = await fetchSandbox(
    'pro_03_offerers',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer'
  )
  const offererSelect = Selector('#offererId')
  const offererOption = offererSelect.find('option')
  const offererDetailLink = Selector(`a[href="/structures/${offerer.id}"]`)

  await navigateToHomeAs(user, createUserRole(user))(t)

  await t
    .click(offererSelect)
    .click(offererOption.withText(offerer.name))
    .click(offererDetailLink)
    .expect(getPathname())
    .match(/\/structures\/([A-Z0-9]*)$/)
})
