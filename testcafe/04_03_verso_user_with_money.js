// $(yarn bin)/testcafe chrome:headless ./testcafe/04_03_verso_user_with_money.js
import { Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { getVersoWallet, getVersoWalletValue } from './helpers/getVersoWallet'
import { ROOT_PATH } from '../src/utils/config'

let offerTitle = null
let offerSubTitle = null
const discoverURL = `${ROOT_PATH}decouverte`
const dragButton = Selector('#dragButton')
const versoOfferName = Selector('#verso-offer-name')
const versoOfferVenue = Selector('#verso-offer-venue')
const bookOfferButton = Selector('#verso-booking-button')
const closeVersoButton = Selector('#deck-close-verso-button')
const openVersoButton = Selector('#deck-open-verso-button')
const alreadyBookedOfferButton = Selector('#verso-already-booked-button')

fixture(`04 Verso`).beforeEach(async t => {
  // given
  const { user } = await fetchSandbox(
    'webapp_04_verso',
    'get_existing_webapp_hbs_user'
  )
  const { mediationId, offer } = await fetchSandbox(
    'webapp_08_booking',
    'get_non_free_thing_offer_with_active_mediation'
  )
  offerTitle = offer.thingName
  offerSubTitle = offer.venueName
  const offerURL = `${discoverURL}/${offer.id}/${mediationId}`
  await t.useRole(createUserRole(user)).navigateTo(offerURL)
  await dragButton.with({ visibilityCheck: true })()
})

test(`L'user doit pouvoir cliquer sur les chevrons pour ouvrir le verso`, async t => {
  await t
    .expect(openVersoButton.exists)
    .ok()
    .click(openVersoButton)
    .expect(closeVersoButton.exists)
    .ok()
})

test(`L'user a de l'argent sur son compte`, async t => {
  await t.click(openVersoButton)

  const versoWallet = await getVersoWallet()
  const versoWalletValue = await getVersoWalletValue()
  await t
    .expect(versoWallet)
    .contains('€')
    .expect(versoWalletValue)
    .gte(0)
})

test(`L'user peut réserver l'Offre`, async t => {
  await t
    .click(openVersoButton)
    .expect(alreadyBookedOfferButton.exists)
    .notOk()
    .expect(bookOfferButton.exists)
    .ok()
    .expect(bookOfferButton.textContent)
    .eql(`J'y vais!`)
})

test('Le titre et le nom du lieu sont affichés', async t => {
  await t
    .click(openVersoButton)
    .expect(versoOfferName.textContent)
    .contains(offerTitle)
    .expect(versoOfferVenue.textContent)
    .eql(offerSubTitle)
})
