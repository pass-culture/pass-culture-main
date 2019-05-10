import { Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const discoverURL = `${ROOT_PATH}decouverte`

const dragButton = Selector('#dragButton')
const openVersoButton = Selector('#deck-open-verso-button')

const versoOfferLabel = Selector('#verso-offer-label')
const versoOfferName = Selector('#verso-offer-name')
const versoOfferVenue = Selector('#verso-offer-venue')

fixture(`04_05 Verso détails de l'offre`)

test('Le titre et le nom du lieu sont affichés ainsi que le type', async t => {
  // given
  const { user, recommendation } = await fetchSandbox(
    'webapp_03_decouverte',
    'get_existing_webapp_user_with_at_least_one_recommendation'
  )

  const offerURL = `${discoverURL}/${recommendation.offerId}`
  await t.useRole(createUserRole(user)).navigateTo(offerURL)
  await dragButton.with({ visibilityCheck: true })()
  const offerTitle = recommendation.offer.name
  const offerVenue = recommendation.offer.venue.name
  const offerType = recommendation.offer.product.offerType.appLabel

  await t
    .click(openVersoButton)

    // Header title
    .expect(versoOfferName.textContent)
    .contains(offerTitle)
    .expect(versoOfferVenue.textContent)
    .eql(offerVenue)

    // Quoi ?
    .expect(versoOfferLabel.textContent)
    .eql(offerType)
})
