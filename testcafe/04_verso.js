import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'
import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import getUserWalletValue from './helpers/getUserWalletValue'

const offerDetailsURL = `${ROOT_PATH}offre/details`
const bookingsDetailsURL = `${ROOT_PATH}reservations/details`
const openProfilePage = Selector('nav ul li a[href="/profil"]')
const sendBookingButton = Selector('#booking-validation-button')
const alreadyBookedOfferButton = Selector('#verso-already-booked-button')
const bookOfferButton = Selector('button').withText('J’y vais !')
const bookingToken = Selector('#booking-booked-token')
const bookingSuccessButton = Selector('#booking-success-ok-button')
const checkReversedIcon = Selector('.ticket-price img')
const bookingErrorReasons = Selector('#booking-error-reasons p')
const dateSelectBox = Selector('#booking-form-date-picker-field')
const myBookingsNavbarButton = Selector('nav ul li a[href="/reservations"]')
const selectableDates = Selector(
  '.react-datepicker__day--selected, .react-datepicker__day:not(.react-datepicker__day--disabled)'
)

let userRole = null
let offerPage = null
let previousWalletValue = null
let currentBookedToken = null

fixture("Etant sur le verso d'une offre,")

test("je peux réserver l'offre", async t => {
  // given
  userRole = await createUserRoleFromUserSandbox(
    'webapp_08_booking',
    'get_existing_webapp_user_can_book_digital_offer'
  )
  const { offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_thing_offer_with_active_mediation'
  )
  offerPage = `${offerDetailsURL}/${offer.id}`
  await t.useRole(userRole).navigateTo(offerPage)

  // when
  await t
    .expect(alreadyBookedOfferButton.exists)
    .notOk()
    .expect(bookOfferButton.exists)
    .ok()
})

test("parcours complet de réservation d'une offre thing", async t => {
  // given
  userRole = await createUserRoleFromUserSandbox(
    'webapp_08_booking',
    'get_existing_webapp_user_can_book_thing_offer'
  )
  const { offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_thing_offer_with_active_mediation'
  )

  offerPage = `${offerDetailsURL}/${offer.id}`

  await t.useRole(userRole).navigateTo(offerPage)

  await t.click(openProfilePage).wait(500)
  previousWalletValue = await getUserWalletValue()
  await t
    .expect(previousWalletValue)
    .gt(0)
    .useRole(userRole)
    .navigateTo(offerPage)
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

  currentBookedToken = await bookingToken.textContent
  currentBookedToken = currentBookedToken.toLowerCase()
  await t
    .click(bookingSuccessButton)
    .expect(checkReversedIcon.exists)
    .ok()
    .click(openProfilePage)

  const currentWalletValue = await getUserWalletValue()
  await t
    .expect(currentWalletValue)
    .gte(0)
    .expect(currentWalletValue)
    .lt(previousWalletValue)

  const bookedOffer = Selector(`.mb-my-booking[data-token="${currentBookedToken}"]`)

  await t
    .click(myBookingsNavbarButton)
    .expect(bookedOffer.exists)
    .ok()
    .click(bookedOffer)
    .expect(getPageUrl())
    .contains(bookingsDetailsURL)
    .expect(checkReversedIcon.exists)
    .ok()
})

test("parcours complet de réservation d'une offre event à date unique", async t => {
  // given
  userRole = await createUserRoleFromUserSandbox(
    'webapp_08_booking',
    'get_existing_webapp_user_can_book_multidates'
  )
  const { offer } = await fetchSandbox('webapp_08_booking', 'get_non_free_event_offer')
  offerPage = `${offerDetailsURL}/${offer.id}`

  await t.useRole(userRole).navigateTo(offerPage)

  // when
  await t.click(openProfilePage).wait(500)
  previousWalletValue = await getUserWalletValue()

  await t
    .expect(previousWalletValue)
    .gt(0)
    .useRole(userRole)
    .navigateTo(offerPage)
    .click(bookOfferButton)
    .click(dateSelectBox)
    .click(selectableDates.nth(0))
    .click(sendBookingButton)
    .expect(bookingErrorReasons.count)
    .eql(0)
    .expect(bookingToken.exists)
    .ok()

  currentBookedToken = await bookingToken.textContent
  await t
    .click(bookingSuccessButton)
    .expect(checkReversedIcon.exists)
    .ok()
    .click(openProfilePage)

  const currentWalletValue = await getUserWalletValue()
  await t
    .expect(currentWalletValue)
    .gte(0)
    .expect(currentWalletValue)
    .lt(previousWalletValue)

  const bookedOffer = Selector(`.mb-my-booking[data-token="${currentBookedToken}"]`)
  await t
    .click(myBookingsNavbarButton)
    .expect(bookedOffer.exists)
    .ok()
    .click(bookedOffer)
    .expect(getPageUrl())
    .contains(bookingsDetailsURL)
    .expect(checkReversedIcon.exists)
    .ok()
})
