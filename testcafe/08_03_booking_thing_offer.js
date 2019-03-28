// $(yarn bin)/testcafe chrome ./testcafe/08_03_booking_thing_offer.js
import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import getMenuWalletValue from './helpers/getMenuWalletValue'
import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import { createUserRole } from './helpers/roles'

let offerPage = null
let offerPageVerso = null
let offerBookingPage = null
let currentBookedToken = null
let previousWalletValue = null
const myProfileURL = `${ROOT_PATH}profil`
const discoverURL = `${ROOT_PATH}decouverte`
const myBookingsURL = `${ROOT_PATH}reservations`

const bookingToken = Selector('#booking-booked-token')
const bookOfferButton = Selector('#verso-booking-button')
const alreadyBookedOfferButton = Selector('#verso-already-booked-button')
const bookingSuccessButton = Selector('#booking-success-ok-button')
const closeMenu = Selector('#main-menu-close-button')
const openMenu = Selector('#deck-footer .profile-button')
const openMenuFromVerso = Selector('#verso-footer .profile-button')
const bookingErrorReasons = Selector('#booking-error-reasons p')
const openVerso = Selector('#deck-open-verso-button')
const timeSelectBox = Selector('#booking-form-time-picker-field')
const dateSelectBox = Selector('#booking-form-date-picker-field')
const sendBookingButton = Selector('#booking-validation-button')
const myBookingMenuButton = Selector('#main-menu-reservations-button')
const profileWalletAllValue = Selector('#profile-wallet-balance-value')

fixture(`08_03 Réservation d'une offre type thing`).beforeEach(async t => {
  const { user } = await fetchSandbox(
    'webapp_08_booking',
    'get_existing_webapp_user_can_book_thing_offer'
  )
  const { mediationId, offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_thing_offer_with_active_mediation'
  )
  offerPage = `${discoverURL}/${offer.id}/${mediationId}`
  offerPageVerso = `${offerPage}/verso`
  offerBookingPage = `${offerPage}/booking`
  await t.useRole(createUserRole(user)).navigateTo(offerPage)
})

test(`Le formulaire de réservation ne contient pas de selecteur de date ou d'horaire`, async t => {
  await t
    .click(openVerso)
    .wait(500)
    .click(bookOfferButton)
    .expect(getPageUrl())
    .eql(offerBookingPage)
    .expect(dateSelectBox.exists)
    .notOk()
    .expect(timeSelectBox.exists)
    .notOk()
})

test(`Parcours complet de réservation d'une offre thing`, async t => {
  await t.click(openMenu).wait(500)
  previousWalletValue = await getMenuWalletValue()
  await t
    .expect(previousWalletValue)
    .gt(0)
    .click(closeMenu)
    .wait(500)
    .click(openVerso)
    .wait(500)
    .expect(alreadyBookedOfferButton.exists)
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
    .eql(offerPage)
    .expect(alreadyBookedOfferButton.textContent)
    .eql(`Réservé`)
    .click(openMenuFromVerso)

  const currentWalletValue = await getMenuWalletValue()
  await t
    .expect(currentWalletValue)
    .gte(0)
    .expect(currentWalletValue)
    .lt(previousWalletValue)
  previousWalletValue = await getMenuWalletValue()

  const bookedOffer = Selector(
    `.booking-item[data-token="${currentBookedToken}"]`
  )
  await t
    .click(myBookingMenuButton)
    .expect(bookedOffer.exists)
    .ok()
    .click(bookedOffer)
    .expect(getPageUrl())
    .eql(offerPageVerso)
    .expect(alreadyBookedOfferButton.textContent)
    .eql(`Réservé`)
})

test(`Je vérifie mes réservations après reconnexion`, async t => {
  const bookedOffer = Selector(
    `.booking-item[data-token="${currentBookedToken}"]`
  )
  await t
    .navigateTo(myBookingsURL)
    .expect(bookedOffer.exists)
    .ok()
    .click(bookedOffer)
    .wait(1000)
    .expect(alreadyBookedOfferButton.textContent)
    .eql(`Réservé`)
    .click(alreadyBookedOfferButton)
    .expect(getPageUrl())
    .eql(myBookingsURL)
})

test(`Je vérifie le montant de mon pass`, async t => {
  const walletInfoSentence = `Il reste ${previousWalletValue} €`
  await t
    .navigateTo(myProfileURL)
    .expect(profileWalletAllValue.textContent)
    .eql(walletInfoSentence)
})

test(`Je ne peux plus réserver cette offre`, async t => {
  await t
    .click(openVerso)
    .wait(500)
    .expect(bookOfferButton.exists)
    .notOk()
    .expect(alreadyBookedOfferButton.exists)
    .ok()
})
