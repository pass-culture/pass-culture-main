import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateToOfferersAs, } from './helpers/navigations'

fixture(`Lorsque je clique sur le menu, je clique sur le lien pour atteindre mes "structures"`)

test('Si j\'ai une structure validée, je clique sur celle-ci afin d\'accéder au détail', async t => {
  // given
  const {user, offerer} = await fetchSandbox(
    'pro_03_offerers',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer'
  )
  const {id: offererId} = offerer
  const offererItem = Selector('.offerer-item')
    .find(`a[href="/structures/${offererId}"]`)
    .parent('.offerer-item')
  const offererItemDetailLink = offererItem
    .find('div.caret')
    .find('a')

  // when
  await navigateToOfferersAs(user)(t)
  await t.click(offererItemDetailLink)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/structures\/([A-Z0-9]*)$/)
})
