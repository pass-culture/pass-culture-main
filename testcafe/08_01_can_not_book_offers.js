import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { getVersoWalletValue } from './helpers/getVersoWallet'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

const discoverURL = `${ROOT_PATH}decouverte`

const bookOfferButton = Selector('#verso-booking-button')
const alreadyBookedOfferButton = Selector('#verso-already-booked-button')
const bookingErrorReasons = Selector('#booking-error-reasons p')
const openVerso = Selector('#deck-open-verso-button')
const sendBookingButton = Selector('#booking-validation-button')

let userRole

fixture("08_01_01 L'utilisateur ne peut pas réserver").beforeEach(async t => {
  userRole = await createUserRoleFromUserSandbox(
    'webapp_08_booking',
    'get_existing_webapp_user_has_no_more_money'
  )
  await t.useRole(userRole)
})

test("Je n'ai plus d'argent", async t => {
  const { mediationId, offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_thing_offer_with_active_mediation'
  )
  const offerPage = `${discoverURL}/${offer.id}/${mediationId}`
  await t.navigateTo(offerPage).click(openVerso)
  const versoWalletValue = await getVersoWalletValue()
  await t
    .expect(versoWalletValue)
    .eql(0)
    .expect(alreadyBookedOfferButton.exists)
    .notOk()
    .expect(bookOfferButton.textContent)
    .match(/([0-9]*\s€J’y vais !)/g)
    .click(bookOfferButton)
    .expect(sendBookingButton.exists)
    .ok()
    .click(sendBookingButton)
    .expect(bookingErrorReasons.nth(1).exists)
    .ok()
    .expect(bookingErrorReasons.nth(1).textContent)
    .eql("Le solde de votre pass n'est pas suffisant pour effectuer cette réservation.")
})
