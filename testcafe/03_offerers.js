import { Selector } from 'testcafe'

import { getPathname } from './helpers/location'
import { navigateToOfferersAs } from './helpers/navigations'
import { fetchSandbox } from './helpers/sandboxes'

fixture('Lorsque je clique sur le menu, je clique sur le lien pour atteindre mes "structures",')

test('si j’ai une structure validée, je clique sur celle-ci afin d’accéder au détail', async t => {
  const { user, offerer } = await fetchSandbox(
    'pro_03_offerers',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer'
  )
  const offererItem = Selector('.offerer-item')
    .find(`a[href="/structures/${offerer.id}"]`)
    .parent('.offerer-item')
  const offererItemDetailLink = offererItem.find('div.caret').find('a')
  await navigateToOfferersAs(user)(t)

  await t
    .click(offererItemDetailLink)
    .expect(getPathname())
    .match(/\/structures\/([A-Z0-9]*)$/)
})
