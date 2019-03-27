// $(yarn bin)/testcafe chrome:headless ./testcafe/04_02_verso_user_already_booked.js
import { Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const discoverURL = `${ROOT_PATH}decouverte`
const dragButton = Selector('#dragButton')
const bookOfferButton = Selector('#verso-booking-button')
const openVersoButton = Selector('#deck-open-verso-button')
const eventAlreadyBookedButton = Selector('#verso-already-booked-button')
const onlineAlreadyBookedButton = Selector('#verso-online-booked-button')

fixture(`04 Verso`)

test(`L'user ne peut plus réserver une offre digitale déjà réservée`, async t => {
  await t
    .click(openVersoButton)
    .expect(bookOfferButton.exists)
    .notOk()
    .expect(onlineAlreadyBookedButton.exists)
    .ok()
    .expect(onlineAlreadyBookedButton.textContent)
    .eql(`Accéder`)
}).before(async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'webapp_04_verso',
    'get_digital_offer_already_booked_and_user_hnmm_93'
  )
  const offerURL = `${discoverURL}/${offer.id}`
  await t.useRole(createUserRole(user)).navigateTo(offerURL)
  await dragButton.with({ visibilityCheck: true })()
})

test(`L'user ne peut plus réserver un event déjà réservé`, async t => {
  await t
    .click(openVersoButton)
    .expect(bookOfferButton.exists)
    .notOk()
    .expect(eventAlreadyBookedButton.exists)
    .ok()
    .expect(eventAlreadyBookedButton.textContent)
    .eql(`Réservé`)
}).before(async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'webapp_04_verso',
    'get_event_already_booked_and_user_hnmm_93'
  )
  const offerURL = `${discoverURL}/${offer.id}`
  await t.useRole(createUserRole(user)).navigateTo(offerURL)
  await dragButton.with({ visibilityCheck: true })()
})
