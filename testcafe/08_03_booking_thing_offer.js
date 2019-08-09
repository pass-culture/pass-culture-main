import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import getMenuWalletValue from './helpers/getMenuWalletValue'
import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

let discoveryCardUrl = null
let discoveryDetailsUrl = null
let currentBookedToken = null
let previousWalletValue = null
const discoverUrl = `${ROOT_PATH}decouverte`
const myBookingsUrl = `${ROOT_PATH}reservations`
const bookingToken = Selector('#booking-booked-token')
const bookOfferButton = Selector('#verso-booking-button')
const checkReversedIcon = Selector('#verso-cancel-booking-button-reserved')
const bookingSuccessButton = Selector('#booking-success-ok-button')
const closeMenu = Selector('#main-menu-fixed-container .close-link')
const openMenu = Selector('#deck-footer .profile-button')
const openMenuFromVerso = Selector('#verso-footer .profile-button')
const bookingErrorReasons = Selector('#booking-error-reasons p')
const openDetails = Selector('#deck-open-verso-button')
const sendBookingButton = Selector('#booking-validation-button')
const myBookingsMenuButton = Selector('#main-menu-navigation a').nth(2)

let userRole

fixture("08_03_01 Réservation d'une offre type thing").beforeEach(async t => {
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_08_booking',
      'get_existing_webapp_user_can_book_thing_offer'
    )
  }
  const { mediationId, offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_thing_offer_with_active_mediation'
  )
  discoveryCardUrl = `${discoverUrl}/${offer.id}/${mediationId}`
  discoveryDetailsUrl = `${discoveryCardUrl}/details`
  await t.useRole(userRole).navigateTo(discoveryCardUrl)
})

test("Parcours complet de réservation d'une offre thing", async t => {
  await t.click(openMenu).wait(500)
  previousWalletValue = await getMenuWalletValue()
  await t
    .expect(previousWalletValue)
    .gt(0)
    .click(closeMenu)
    .wait(500)
    .click(openDetails)
    .wait(500)
    .expect(checkReversedIcon.exists)
    .notOk()
    .expect(bookOfferButton.exists)
    .ok()
    .click(bookOfferButton)
    .expect(sendBookingButton.exists)
    .ok()
    .click(sendBookingButton)
    .expect(bookingErrorReasons.nth(0).exists)
    .notOk()
    .expect(bookingToken.exists)
    .ok()

  currentBookedToken = await bookingToken.textContent
  await t
    .click(bookingSuccessButton)
    .expect(getPageUrl())
    .eql(discoveryDetailsUrl)
    .expect(checkReversedIcon.exists)
    .ok()
    .click(openMenuFromVerso)

  const currentWalletValue = await getMenuWalletValue()
  await t
    .expect(currentWalletValue)
    .gte(0)
    .expect(currentWalletValue)
    .lt(previousWalletValue)
  previousWalletValue = await getMenuWalletValue()

  const bookedOffer = Selector(`.my-bookings-my-booking[data-token="${currentBookedToken}"]`)
  await t
    .click(myBookingsMenuButton)
    .expect(bookedOffer.exists)
    .ok()
    .click(bookedOffer)
    .expect(getPageUrl())
    .match(new RegExp(`${myBookingsUrl}/details/([A-Z0-9]+)`))
    .expect(checkReversedIcon.exists)
    .ok()
})
