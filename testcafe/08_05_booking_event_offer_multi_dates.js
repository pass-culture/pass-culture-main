import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import getMenuWalletValue from './helpers/getMenuWalletValue'
import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

let discoveryCardUrl = null
let discoverDetailsUrl = null
let currentBookedToken = null
let currentSelectedTime = null
let previousWalletValue = null
const discoverUrl = `${ROOT_PATH}decouverte`
const myBookingsUrl = `${ROOT_PATH}reservations`

const bookingToken = Selector('#booking-booked-token')
const bookOfferButton = Selector('#verso-booking-button')
const checkReversedIcon = Selector('#verso-cancel-booking-button-reserved')
const bookingSuccessButton = Selector('#booking-success-ok-button')
const closeMenu = Selector('#main-menu-fixed-container .close-link')
const openMenuFromVerso = Selector('#verso-footer .profile-button')
const bookingErrorReasons = Selector('#booking-error-reasons p')
const openVerso = Selector('#deck-open-verso-button')
const timeSelectBox = Selector('#booking-form-time-picker-field')
const dateSelectBox = Selector('#booking-form-date-picker-field')
const sendBookingButton = Selector('#booking-validation-button')
const myBookingsMenuButton = Selector('#main-menu-navigation a').nth(2)
const pickerPopper = Selector('#datepicker-popper-container')
const selectableDates = pickerPopper.find(
  '.react-datepicker__day:not(.react-datepicker__day--disabled)'
)
const selectedTime = timeSelectBox.find('.ant-select-selection-selected-value')

let userRole

fixture("08_05_01 Réservation d'une offre type event à dates multiple").beforeEach(async t => {
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_08_booking',
      'get_existing_webapp_user_can_book_multidates'
    )
  }
  const { mediationId, offer } = await fetchSandbox('webapp_08_booking', 'get_non_free_event_offer')
  discoveryCardUrl = `${discoverUrl}/${offer.id}/${mediationId || 'vide'}`
  discoverDetailsUrl = `${discoveryCardUrl}/details`
  await t
    .useRole(userRole)
    .navigateTo(discoveryCardUrl)
    .click(openVerso)
})

test("Parcours complet de réservation d'une offre event à date unique", async t => {
  await t.click(openMenuFromVerso).wait(500)
  previousWalletValue = await getMenuWalletValue()
  await t
    .expect(previousWalletValue)
    .gt(0)
    .click(closeMenu)
    .click(bookOfferButton)
    .click(dateSelectBox)
    .click(selectableDates.nth(0))

  currentSelectedTime = await selectedTime.textContent
  currentSelectedTime = currentSelectedTime.slice(0, 5)

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
