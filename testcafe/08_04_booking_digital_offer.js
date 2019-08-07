import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import getMenuWalletValue from './helpers/getMenuWalletValue'
import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

let discoveryCardUrl = null
let discoveryDetailsUrl = null
let discoveryBookingUrl = null
let currentBookedToken = null
let previousWalletValue = null
const myProfileUrl = `${ROOT_PATH}profil`
const discoverUrl = `${ROOT_PATH}decouverte`
const myBookingsUrl = `${ROOT_PATH}reservations`

const dragButton = Selector('#dragButton')
const onlineOfferLabel = Selector('#dragButton .clue div')
const onlineOfferFinishable = Selector('#dragButton .clue .finishable')
const bookingOnlineButton = Selector('#booking-online-booked-button')
const bookOfferButton = Selector('#verso-booking-button')
const onlineBookedOfferButton = Selector('#verso-online-booked-button')
const bookingSuccessButton = Selector('#booking-success-ok-button')
const closeMenu = Selector('#main-menu-fixed-container .close-link')
const openMenu = Selector('#deck-footer .profile-button')
const openMenuFromVerso = Selector('#verso-footer .profile-button')
const bookingErrorReasons = Selector('#booking-error-reasons p')
const openVerso = Selector('#deck-open-verso-button')
const timeSelectBox = Selector('#booking-form-time-picker-field')
const dateSelectBox = Selector('#booking-form-date-picker-field')
const sendBookingButton = Selector('#booking-validation-button')
const myBookingsMenuButton = Selector('#main-menu-navigation a').nth(2)
const profileWalletAllValue = Selector('#profile-wallet-balance-value')

let userRole
fixture("08_04_01 Réservation d'une offre type digitale").beforeEach(async t => {
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_08_booking',
      'get_existing_webapp_user_can_book_digital_offer'
    )
  }
  const { mediationId, offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_digital_offer'
  )

  discoveryCardUrl = `${discoverUrl}/${offer.id}/${mediationId || 'vide'}`
  discoveryDetailsUrl = `${discoveryCardUrl}/details`
  discoveryBookingUrl = `${discoveryDetailsUrl}/reservation`
  await t.useRole(userRole).navigateTo(discoveryCardUrl)
})

test("Il s'agit d'une offre en ligne qui n'est pas terminée", async t => {
  await dragButton.with({ visibilityCheck: true })()
  await t
    .expect(onlineOfferLabel.nth(1).textContent)
    .eql('offre en ligne')
    .expect(onlineOfferFinishable.exists)
    .notOk()
})

test("Le formulaire de réservation ne contient pas de sélecteur de date ou d'horaire", async t => {
  await t
    .click(openVerso)
    .wait(500)
    .click(bookOfferButton)
    .expect(getPageUrl())
    .eql(discoveryBookingUrl)
    .wait(500)
    .expect(dateSelectBox.exists)
    .notOk()
    .expect(timeSelectBox.exists)
    .notOk()
})

test("Parcours complet de réservation d'une offre digitale", async t => {
  await t.click(openMenu).wait(500)
  previousWalletValue = await getMenuWalletValue()
  await t
    .expect(previousWalletValue)
    .gt(0)
    .click(closeMenu)
    .click(openVerso)
    .wait(500)
    .expect(onlineBookedOfferButton.exists)
    .notOk()
    .expect(bookOfferButton.exists)
    .ok()
    .click(bookOfferButton)
    .expect(sendBookingButton.exists)
    .ok()
    .click(sendBookingButton)
    .expect(bookingErrorReasons.count)
    .eql(0)
    .wait(1000)
    .expect(bookingOnlineButton.exists)
    .ok()

  currentBookedToken = await bookingOnlineButton.getAttribute('data-token')
  await t
    .click(bookingSuccessButton)
    .wait(500)
    .expect(getPageUrl())
    .eql(discoveryDetailsUrl)
    .expect(onlineBookedOfferButton.textContent)
    .eql(`Accéder`)
    .click(openMenuFromVerso)
    .wait(500)

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
    .expect(onlineBookedOfferButton.textContent)
    .eql(`Accéder`)
})

test('Je vérifie mes réservations après reconnexion', async t => {
  const bookedOffer = Selector(`.my-bookings-my-booking[data-token="${currentBookedToken}"]`)
  await t
    .navigateTo(myBookingsUrl)
    .expect(bookedOffer.exists)
    .ok()
    .click(bookedOffer)
    .expect(onlineBookedOfferButton.textContent)
    .eql(`Accéder`)
    .click(onlineBookedOfferButton)
    .expect(getPageUrl())
    .notEql(myBookingsUrl)
})

test('Je vérifie le montant de mon pass', async t => {
  const walletInfoSentence = `Il reste ${previousWalletValue} €`
  await t
    .navigateTo(myProfileUrl)
    .expect(profileWalletAllValue.textContent)
    .eql(walletInfoSentence)
})

test('Je ne peux plus réserver cette offre', async t => {
  await t
    .click(openVerso)
    .expect(bookOfferButton.exists)
    .notOk()
    .expect(onlineBookedOfferButton.exists)
    .ok()
})
