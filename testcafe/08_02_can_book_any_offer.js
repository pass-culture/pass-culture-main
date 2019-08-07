import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import getMenuWalletValue from './helpers/getMenuWalletValue'
import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

let discoveryCardUrl = null
let discoveryBookingUrl = null
let previousWalletValue = null
const discoverUrl = `${ROOT_PATH}decouverte`
const myBookingsUrl = `${ROOT_PATH}reservations`

const alreadyBookedOfferButton = Selector('#verso-already-booked-button')
const bookOfferButton = Selector('#verso-booking-button')
const myBooking = Selector('.my-bookings-my-booking')
const closeMenu = Selector('#main-menu-fixed-container .close-link')
const menuReservations = Selector('.navlink').withText('Mes réservations')
const openMenu = Selector('#deck-footer .profile-button')
const openVerso = Selector('#deck-open-verso-button')
const sendBookingButton = Selector('#booking-validation-button')

let userRole

fixture("08_02_01 L'user peut réserver n'importe quelle offre").beforeEach(async t => {
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_08_booking',
      'get_existing_webapp_user_can_book_digital_offer'
    )
  }
  // BE CAREFUL: for now this test needs to be launched with
  // a pc sandbox -n industrial just triggered and cannot be triggered twice
  // TODO: this offer should be in the get_existing_webapp_user_can_book_multidates package
  // and should garanty that for this user there is no Booking or a isCancelled Booking
  // associated.
  const { mediationId, offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_thing_offer_with_active_mediation'
  )
  discoveryCardUrl = `${discoverUrl}/${offer.id}/${mediationId}`
  discoveryBookingUrl = `${discoveryCardUrl}/details/reservation`
  await t.useRole(userRole).navigateTo(discoveryCardUrl)
})

test("J'ai de l'argent sur mon pass", async t => {
  await t.click(openMenu).wait(500)
  previousWalletValue = await getMenuWalletValue()
  await t
    .expect(previousWalletValue)
    .gt(0)
    .click(closeMenu)
})

test("Je peux réserver l'offre", async t => {
  await t
    .click(openVerso)
    .wait(500)
    .expect(alreadyBookedOfferButton.exists)
    .notOk()
    .expect(bookOfferButton.textContent)
    .contains(`J’y vais !`)
    .click(bookOfferButton)
    .expect(getPageUrl())
    .eql(discoveryBookingUrl)
    .expect(sendBookingButton.exists)
    .ok()
    .click(sendBookingButton)
})

test("Je vois l'offre dans 'mes réservations' et je peux cliquer dessus pour revenir à la page 'Mes réservations'", async t => {
  await t
    .click(openMenu)
    .click(menuReservations)
    .expect(getPageUrl())
    .eql(myBookingsUrl)
    .click(myBooking)
    .expect(getPageUrl())
    .match(new RegExp(`${myBookingsUrl}/details/([A-Z0-9]+)`))
})
