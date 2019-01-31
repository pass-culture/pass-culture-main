import { Selector } from 'testcafe'

import { navigateToOfferAs } from './helpers/navigations'
import {
  EXISTING_EVENT_OFFER_WITH_EVENT_OCCURRENCE_WITH_STOCK_WITH_MEDIATION_WITH_NO_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN,
  EXISTING_EVENT_OFFER_WITH_EVENT_OCCURRENCE_WITH_STOCK_WITH_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN,
  EXISTING_EVENT_OFFER_WITH_NO_EVENT_OCCURRENCE_WITH_NO_STOCK_WITH_NO_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN,
  EXISTING_THING_OFFER_WITH_STOCK_WITH_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN,
  EXISTING_VIRTUAL_THING_OFFER_WITH_NO_STOCK_WITH_NO_MEDIATION_WITH_NO_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN,
} from './helpers/offers'
import { EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER } from './helpers/users'

const addAnchor = Selector('#add-occurrence-or-stock')
const availableInput = Selector('input[name="available"]')
const manageStockAnchor = Selector('a.manage-stock')
const submitButton = Selector('button.button.submitStep')
const priceInput = Selector('input[name="price"]')

fixture(`OfferPage Gestion A | Créer des dates et des stocks`)

test("Je peux créer une occurrence et un stock d'événement d'une offre vide", async t => {
  // given
  await navigateToOfferAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_EVENT_OFFER_WITH_NO_EVENT_OCCURRENCE_WITH_NO_STOCK_WITH_NO_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)

  // when
  await t.click(manageStockAnchor).click(addAnchor)

  // then
  let location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion&date=nouvelle')

  // when
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .match(/\?gestion&date=([A-Z0-9]*)&stock=nouveau$/)

  // when
  await t.typeText(priceInput, '10').typeText(availableInput, '50')
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion')
})

test('Je peux créer une autre occurrence et un autre stock', async t => {
  // given
  await navigateToOfferAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_EVENT_OFFER_WITH_EVENT_OCCURRENCE_WITH_STOCK_WITH_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)

  // when
  await t.click(manageStockAnchor).click(addAnchor)

  // then
  let location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion&date=nouvelle')

  // when
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .match(/\?gestion&date=([A-Z0-9]*)&stock=nouveau$/)

  // when
  await t.typeText(priceInput, '10').typeText(availableInput, '50')
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion')
})

test('Je peux créer une occurrence en utilisant la touche Entrée', async t => {
  // given
  await navigateToOfferAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_EVENT_OFFER_WITH_EVENT_OCCURRENCE_WITH_STOCK_WITH_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)

  // when
  await t.click(manageStockAnchor).pressKey('Enter')

  // then
  let location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion&date=nouvelle')

  // when
  await t.pressKey('Enter')

  // then
  location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .match(/\?gestion&date=([A-Z0-9]*)&stock=nouveau$/)

  // when
  await t.pressKey('Enter')

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.search).match(/\?gestion$/)
})

test('Je peux femer la fenêtre en utilisant la touche Escape', async t => {
  // given
  await navigateToOfferAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_EVENT_OFFER_WITH_EVENT_OCCURRENCE_WITH_STOCK_WITH_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)

  // when
  await t.click(manageStockAnchor).pressKey('esc')

  // then
  let location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .eql('')
    .expect(location.href)
    .match(/offres\/[A-Z0-9]+/i)
})

test('Je peux femer la fenêtre en cliquant sur le bouton', async t => {
  // given
  const scheduleCloseButton = Selector('button.button').withText('Fermer')
  await navigateToOfferAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_EVENT_OFFER_WITH_EVENT_OCCURRENCE_WITH_STOCK_WITH_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)

  // when
  await t.click(manageStockAnchor).click(scheduleCloseButton)

  // then
  let location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .eql('')
    .expect(location.href)
    .match(/offres\/[A-Z0-9]+/i)
})

test('Je peux interrompre la saisie en utilisant la touche Escape', async t => {
  // given
  await navigateToOfferAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_EVENT_OFFER_WITH_EVENT_OCCURRENCE_WITH_STOCK_WITH_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)

  // when
  await t.click(manageStockAnchor).pressKey('Enter')

  // then
  let location = await t.eval(() => window.location)
  await t.expect(location.search).eql('?gestion&date=nouvelle')

  // when
  await t.pressKey('esc')

  // then
  location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .eql('?gestion')
    .expect(location.href)
    .match(/offres\/[A-Z0-9]+/i)
})

test('Je ne peux pas de rentrer un nouveau stock pour un objet avec déjà un stock', async t => {
  // given
  await navigateToOfferAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_THING_OFFER_WITH_STOCK_WITH_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)

  // when
  await t.click(manageStockAnchor)

  // then
  await t.expect(addAnchor.visible).notOk()
})

fixture(`OfferPage Gestion B | Avertissement pour les offres sans iban`)

const infoDiv = Selector('div.info')
const confirmationButton = infoDiv.find('button')

test("J'ai une info quand je rentre un prix non nul pour l'objet d'une structure et un lieu sans iban", async t => {
  // given
  await navigateToOfferAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_VIRTUAL_THING_OFFER_WITH_NO_STOCK_WITH_NO_MEDIATION_WITH_NO_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)
  await t.click(manageStockAnchor).click(addAnchor)

  // when
  await t.typeText(priceInput, '10').click(availableInput)

  // then
  await t.expect(infoDiv.visible).ok()

  // when
  await t.click(confirmationButton).typeText(availableInput, '50')
  await t.click(submitButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.search).match(/\?gestion$/)
})

test("J'ai une info quand je rentre un prix non nul pour l'évènement d'une structure et un lieu sans iban", async t => {
  // given
  await navigateToOfferAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_EVENT_OFFER_WITH_EVENT_OCCURRENCE_WITH_STOCK_WITH_MEDIATION_WITH_NO_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)
  await t.click(manageStockAnchor).click(addAnchor)
  await t.click(submitButton)

  // when
  await t.typeText(priceInput, '10').click(availableInput)

  // then
  await t.expect(infoDiv.visible).ok()

  // when
  await t.click(confirmationButton).typeText(availableInput, '50')
  await t.click(submitButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.search).match(/\?gestion$/)
})

fixture`OfferPage Gestion C | Modifier des dates et des stocks`

test('Je peux modifier une occurrence et un stock', async t => {
  // given
  const editAnchor = Selector('a.edit-stock:first-child')
  const beginInput = Selector('input.date')
  const datePicker = Selector('.react-datepicker')
  const datePickerLastDay = Selector(
    '.react-datepicker__week:last-child .react-datepicker__day:last-child'
  )
  await navigateToOfferAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_EVENT_OFFER_WITH_EVENT_OCCURRENCE_WITH_STOCK_WITH_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)
  await t.click(manageStockAnchor)

  // when
  await t.click(editAnchor)

  // then
  let location = await t.eval(() => window.location)
  await t.expect(location.search).match(/\?gestion&date=([A-Z0-9]*)$/)
  await t
    .expect(beginInput.exists)
    .ok()
    .expect(datePicker.exists)
    .notOk()
    .click(beginInput)
    .expect(datePicker.exists)
    .ok()
    .click(datePickerLastDay)
    .expect(datePicker.exists)
    .notOk()

  // when
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  await t
    .expect(location.search)
    .match(/\?gestion&date=([A-Z0-9]*)&stock=([A-Z0-9]*|nouveau)$/)

  // when
  await t.typeText(priceInput, '15')
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.search).match(/\?gestion$/)
})
