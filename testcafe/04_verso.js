import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'
import getPageUrl from './helpers/getPageUrl'

import { ROOT_PATH } from '../src/utils/config'
import getMenuWalletValue from './helpers/getMenuWalletValue'

const discoverURL = `${ROOT_PATH}decouverte`
const bookingsDetailsURL = `${ROOT_PATH}reservations/details`

const openVersoButton = Selector('#deck-open-verso-button')

const openDeckMenu = Selector('#deck-footer .profile-button')
const sendBookingButton = Selector('#booking-validation-button')
const alreadyBookedOfferButton = Selector('#verso-already-booked-button')
const bookOfferButton = Selector('#verso-booking-button')

const bookingToken = Selector('#booking-booked-token')
const bookingSuccessButton = Selector('#booking-success-ok-button')
const checkReversedIcon = Selector('#verso-cancel-booking-button-reserved')
const closeMenu = Selector('#main-menu-fixed-container .close-link')
const openMenuFromVerso = Selector('#verso-footer .profile-button')
const bookingErrorReasons = Selector('#booking-error-reasons p')
const dateSelectBox = Selector('#booking-form-date-picker-field')
const myBookingsMenuButton = Selector('#main-menu-navigation a').nth(2)

const selectableDates = Selector(
  '.react-datepicker__day--selected, .react-datepicker__day:not(.react-datepicker__day--disabled)'
)

let offerPage = null
let offerPageDetails = null
let userRole = null
let discoveryCardUrl = null
let discoverDetailsUrl = null
let previousWalletValue = null
let currentBookedToken = null

fixture("Etant sur le verso d'une offre,")

test("Je peux réserver l'offre", async t => {
  // given
  userRole = await createUserRoleFromUserSandbox(
    'webapp_08_booking',
    'get_existing_webapp_user_can_book_digital_offer'
  )
  const { mediationId, offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_thing_offer_with_active_mediation'
  )
  offerPage = `${discoverURL}/${offer.id}/${mediationId}`
  await t.useRole(userRole).navigateTo(offerPage)

  // when
  await t.click(openVersoButton).wait(500)

  await t
    .expect(alreadyBookedOfferButton.exists)
    .notOk()
    .expect(bookOfferButton.textContent)
    .contains(`J’y vais !`)
})

test("Parcours complet de réservation d'une offre thing", async t => {
  // given
  userRole = await createUserRoleFromUserSandbox(
    'webapp_08_booking',
    'get_existing_webapp_user_can_book_thing_offer'
  )
  const { mediationId, offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_thing_offer_with_active_mediation'
  )
  offerPage = `${discoverURL}/${offer.id}/${mediationId}`
  offerPageDetails = `${offerPage}/details`

  await t.useRole(userRole).navigateTo(offerPage)

  await t.click(openDeckMenu).wait(500)
  previousWalletValue = await getMenuWalletValue()
  await t
    .expect(previousWalletValue)
    .gt(0)
    .click(closeMenu)
    .wait(500)
    .click(openVersoButton)
    .wait(500)

  await t
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

  currentBookedToken = await bookingToken.textContent.toLowerCase()
  await t
    .click(bookingSuccessButton)
    .expect(getPageUrl())
    .eql(offerPageDetails)
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

  const bookedOffer = Selector(`.mb-my-booking[data-token="${currentBookedToken}"]`)

  await t
    .click(myBookingsMenuButton)
    .expect(bookedOffer.exists)
    .ok()
    .click(bookedOffer)
    .expect(getPageUrl())
    .contains(bookingsDetailsURL)
    .expect(checkReversedIcon.exists)
    .ok()
})

test("Parcours complet de réservation d'une offre event à date unique", async t => {
  // given
  userRole = await createUserRoleFromUserSandbox(
    'webapp_08_booking',
    'get_existing_webapp_user_can_book_multidates'
  )
  const { mediationId, offer } = await fetchSandbox('webapp_08_booking', 'get_non_free_event_offer')
  discoveryCardUrl = `${discoverURL}/${offer.id}/${mediationId || 'vide'}`
  discoverDetailsUrl = `${discoveryCardUrl}/details`

  await t
    .useRole(userRole)
    .navigateTo(discoveryCardUrl)
    .click(openVersoButton)

  // when
  await t.click(openMenuFromVerso).wait(500)
  previousWalletValue = await getMenuWalletValue()
  await t
    .expect(previousWalletValue)
    .gt(0)
    .click(closeMenu)
    .click(bookOfferButton)
    .click(dateSelectBox)
    .click(selectableDates.nth(0))

  await t
    .click(sendBookingButton)
    .expect(bookingErrorReasons.count)
    .eql(0)
    .expect(bookingToken.exists)
    .ok()

  currentBookedToken = await bookingToken.textContent
  await t
    .click(bookingSuccessButton)
    .expect(getPageUrl())
    .eql(discoverDetailsUrl)
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

  const bookedOffer = Selector(`.mb-my-booking[data-token="${currentBookedToken}"]`)
  await t
    .click(myBookingsMenuButton)
    .expect(bookedOffer.exists)
    .ok()
    .click(bookedOffer)
    .expect(getPageUrl())
    .contains(bookingsDetailsURL)
    .expect(checkReversedIcon.exists)
    .ok()
})
