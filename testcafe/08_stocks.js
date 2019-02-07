import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateToOfferAs } from './helpers/navigations'

const addAnchor = Selector('#add-occurrence-or-stock')
const backButton = Selector('a.back-button')
const availableInput = Selector('input[name="available"]')
const closeManagerButton = Selector('#close-manager')
const manageStockAnchor = Selector('a.manage-stock')
const submitButton = Selector('button.button.submitStep')
const priceInput = Selector('input[name="price"]')

fixture('OfferPage Gestion A | Créer des dates et des stocks')

// TODO: // then
// const infoForManagerSpan = Selector('span.nb-dates')
// await t.expect(infoForManagerSpan.innerText).eql('1 stock')

test("Je peux créer une occurrence et un stock d'événement d'une offre vide", async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_no_occurrence'
  )
  await navigateToOfferAs(user, offer)(t)

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
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_occurrence'
  )
  await navigateToOfferAs(user, offer)(t)

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
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_occurrence'
  )
  await navigateToOfferAs(user, offer)(t)

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
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_occurrence'
  )
  await navigateToOfferAs(user, offer)(t)

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
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_occurrence'
  )
  await navigateToOfferAs(user, offer)(t)

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
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_occurrence'
  )
  await navigateToOfferAs(user, offer)(t)

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

test('Je ne peux pas rentrer un nouveau stock pour un objet avec déjà un stock', async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_thing_offer_with_stock'
  )

  await navigateToOfferAs(user, offer)(t)

  // when
  await t.click(manageStockAnchor)

  // then
  await t.expect(addAnchor.visible).notOk()
})

fixture('OfferPage Gestion B | Avertissement pour les offres sans iban')

const infoDiv = Selector('div.info')
const confirmationButton = infoDiv.find('button')

test("J'ai une info quand je rentre un prix non nul pour l'objet d'une structure et un lieu sans iban", async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_no_iban_validated_user_offerer_with_thing_offer_with_no_stock'
  )
  await navigateToOfferAs(user, offer)(t)
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
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_no_iban_validated_user_offerer_with_event_offer'
  )
  await navigateToOfferAs(user, offer)(t)
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

fixture('OfferPage Gestion C | Modifier des dates et des stocks')

test('Je peux modifier une occurrence et un stock', async t => {
  // given
  const editAnchor = Selector('a.edit-stock:first-child')
  const beginInput = Selector('input.date')
  const datePicker = Selector('.react-datepicker')
  const datePickerLastDay = Selector(
    '.react-datepicker__week:last-child .react-datepicker__day:last-child'
  )
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_occurrence'
  )
  await navigateToOfferAs(user, offer)(t)
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

test('Je peux aller sur le stock manager et revenir aux offres pour chercher une nouvelle offre sans bug de modal en appuyant sur enter', async t => {
  // given
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_occurrence'
  )
  await navigateToOfferAs(user, offer)(t)
  const searchInput = Selector('#search')
  await t
    .click(manageStockAnchor)
    .click(closeManagerButton)
    .click(backButton)
    .typeText(searchInput, 'blabla')

  // when
  await t.pressKey('Enter')

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
})

fixture.skip('TODO: OfferPage Gestion D | Effacer des dates et des stocks')

test('Je peux effacer une date et son stock', async t => {
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_occurrence'
  )
  await navigateToOfferAs(user, offer)(t)
})
