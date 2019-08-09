import { Selector } from 'testcafe'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

const discoverURL = `${ROOT_PATH}decouverte`
const dragButton = Selector('#dragButton')
const bookOfferButton = Selector('#verso-booking-button')
const openVersoButton = Selector('#deck-open-verso-button')
const alreadyBookedOfferButton = Selector('#verso-already-booked-button')

let userRole

fixture("04_03_01 Verso | L'utilisateur peut réserver l'offre payante").beforeEach(async t => {
  // given
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_04_verso',
      'get_existing_webapp_hbs_user'
    )
  }

  const { mediationId, offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_thing_offer_with_active_mediation'
  )
  const offerURL = `${discoverURL}/${offer.id}/${mediationId}`
  await t.useRole(userRole).navigateTo(offerURL)
  await dragButton.with({ visibilityCheck: true })()
})

test("L'utilisateur peut réserver l'Offre", async t => {
  await t
    .click(openVersoButton)
    .expect(alreadyBookedOfferButton.exists)
    .notOk()
    .expect(bookOfferButton.exists)
    .ok()
    .expect(bookOfferButton.textContent)
    .match(/([0-9]*\s€J’y vais !)/g)
})
