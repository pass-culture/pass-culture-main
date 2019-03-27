import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import getMenuWalletValue from './helpers/getMenuWalletValue'
import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import { createUserRole } from './helpers/roles'

let offerPage = null
let offerBookingPage = null
let previousWalletValue = null
const discoverURL = `${ROOT_PATH}decouverte`

const alreadyBookedOfferButton = Selector('#verso-already-booked-button')
const bookOfferButton = Selector('#verso-booking-button')
const bookingItem = Selector('.booking-item')
const closeMenu = Selector('#main-menu-close-button')
const closeBookingButton = Selector('#booking-close-button')
const menuReservations = Selector('.navlink').withText('Mes Réservations')
const openMenu = Selector('#deck-footer .profile-button')
const openVerso = Selector('#deck-open-verso-button')
const sendBookingButton = Selector('#booking-validation-button')

fixture(`08_02 L'user peut reserver n'importe quelle offre`).beforeEach(
  async t => {
    const { user } = await fetchSandbox(
      'webapp_08_booking',
      'get_existing_webapp_user_can_book_digital_offer'
    )
    const { offer } = await fetchSandbox(
      'webapp_08_booking',
      'get_non_free_thing_offer'
    )
    offerPage = `${discoverURL}/${offer.id}`
    offerBookingPage = `${offerPage}/booking`
    await t.useRole(createUserRole(user)).navigateTo(offerPage)
  }
)

test(`J'ai de l'argent sur mon pass`, async t => {
  await t.click(openMenu).wait(500)
  previousWalletValue = await getMenuWalletValue()
  await t
    .expect(previousWalletValue)
    .gt(0)
    .click(closeMenu)
})

test(`Je peux réserver l'offre`, async t => {
  await t
    .click(openVerso)
    .wait(500)
    .expect(alreadyBookedOfferButton.exists)
    .notOk()
    .expect(bookOfferButton.textContent)
    .eql(`J'y vais!`)
    .click(bookOfferButton)
    .expect(getPageUrl())
    .eql(offerBookingPage)
    .expect(sendBookingButton.exists)
    .ok()
})

test(`Je vois l'offre dans "mes réservations" et je peux cliquer dessus pour revenir à la page booking`, async t => {
  await t
    .click(openMenu)
    .click(menuReservations)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}reservations`)
    .click(bookingItem)
    .expect(getPageUrl())
    .match(/\/decouverte\/.*\/verso$/)
})

test(`Je peux cliquer sur annuler pour fermer le formulaire de réservation`, async t => {
  await t
    .click(openVerso)
    .wait(500)
    .click(bookOfferButton)
    .expect(getPageUrl())
    .eql(offerBookingPage)
    .expect(closeBookingButton.exists)
    .ok()
})
