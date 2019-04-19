// $(yarn bin)/testcafe chrome:headless ./testcafe/04_02_verso_user_already_booked.js
import { Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const discoverURL = `${ROOT_PATH}decouverte`
const dragButton = Selector('#dragButton')
const sharePopin = Selector('#share-popin')
const cancelBookButton = Selector('#verso-cancel-booking-button')
const bookOfferButton = Selector('#verso-booking-button')
const openVersoButton = Selector('#deck-open-verso-button')
const onlineAlreadyBookedButton = Selector('#verso-online-booked-button')
const sharePopinTitle = Selector('#share-popin-fixed-container h3')
const sharePopinYesButton = Selector('#popin-cancel-booking-yes')
const sharePopinNoButton = Selector('#popin-cancel-booking-no')
const bookingCheckIcon = Selector(
  '#verso-cancel-booking-button .icon-ico-check'
)

let offerTitle

fixture(`04_02 Verso offre déjà réservée`)

test(`L'user ne peut plus réserver une offre digitale déjà réservée`, async t => {
  await t
    .click(openVersoButton)
    .expect(bookOfferButton.exists)
    .notOk()
    .expect(onlineAlreadyBookedButton.exists)
    .ok()
    .expect(cancelBookButton.exists)
    .ok()
    .expect(cancelBookButton.textContent)
    .match(/([0-9]*\s€Annuler)/g)
    .expect(onlineAlreadyBookedButton.textContent)
    .eql(`Accéder`)
}).before(async t => {
  // given
  const { mediation, offer, user } = await fetchSandbox(
    'webapp_04_verso',
    'get_digital_offer_with_active_mediation_already_booked_and_user_hnmm_93'
  )
  const offerURL = `${discoverURL}/${offer.id}/${mediation.id}`
  await t.useRole(createUserRole(user)).navigateTo(offerURL)
  await dragButton.with({ visibilityCheck: true })()
})

fixture.skip(`04_02 Verso annulation d'un réservation`).beforeEach(async t => {
  // given
  const { mediation, offer, user } = await fetchSandbox(
    'webapp_04_verso',
    'get_event_offer_with_active_mediation_already_booked_but_cancellable_and_user_hnmm_93'
  )
  offerTitle = offer.thingName
  const offerURL = `${discoverURL}/${offer.id}/${mediation.id}`

  await t.useRole(createUserRole(user)).navigateTo(offerURL)
  await dragButton.with({ visibilityCheck: true })()
})

test(`L'user ne peut plus réserver un event déjà réservé`, async t => {
  await t
    .click(openVersoButton)
    .expect(bookOfferButton.exists)
    .notOk()
    .expect(cancelBookButton.exists)
    .ok()
    .expect(cancelBookButton.textContent)
    .match(/([0-9]*\s€Annuler)/g)
    .expect(onlineAlreadyBookedButton.exists)
    .notOk()
    .expect(bookingCheckIcon.exists)
    .ok()
})

test(`Je décide de ne plus vouloir annuler ma réservation`, async t => {
  await t
    .click(openVersoButton)
    .expect(bookOfferButton.exists)
    .notOk()
    .click(cancelBookButton)
    .expect(sharePopin.hasClass('transition-entered'))
    .ok()
    .expect(sharePopinNoButton.textContent)
    .eql('Non')
    .click(sharePopinNoButton)
    .wait(500)
    .expect(sharePopin.hasClass('transition-exited'))
    .ok()
})

test(`Parcours d'annulation d'une réservation`, async t => {
  await t
    .click(openVersoButton)
    .click(cancelBookButton)
    .expect(bookingCheckIcon.exists)
    .ok()
    .expect(sharePopin.hasClass('transition-entered'))
    .ok()
    .expect(sharePopinTitle.textContent)
    .eql(offerTitle)
    .expect(sharePopinYesButton.textContent)
    .eql('Oui')
    .click(sharePopinYesButton)
    .expect(sharePopinTitle.textContent)
    .notEql('Annulation impossible')
})

test(`Apres reservation, la coche de réservation a disparu, le bouton affiche toujours annuler`, async t => {
  await t
    .click(openVersoButton)
    .expect(bookingCheckIcon.exists)
    .notOk()
    .expect(cancelBookButton.textContent)
    .match(/([0-9]*\s€Annuler)/g)
})
