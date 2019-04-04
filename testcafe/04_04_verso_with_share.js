// $(yarn bin)/testcafe chrome ./testcafe/04_04_verso_with_share.js
import { Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const discoverURL = `${ROOT_PATH}decouverte`

const dragButton = Selector('#dragButton')
const shareButton = Selector('#verso-share-button')
const openVersoButton = Selector('#deck-open-verso-button')
const sharePopin = Selector('#share-popin-fixed-container')

fixture(`04_04 Verso partage de l'offre`).beforeEach(async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'webapp_04_verso',
    'get_digital_offer_with_active_mediation_already_booked_and_user_hnmm_93'
  )
  const offerURL = `${discoverURL}/${offer.id}`
  await t.useRole(createUserRole(user)).navigateTo(offerURL)
  await dragButton.with({ visibilityCheck: true })()
})

test('Je peux cliquer sur le bouton de partage', async t => {
  await t
    .click(openVersoButton)
    .click(shareButton)
    .wait(500)
    .expect(sharePopin.exists)
    .ok()
})
