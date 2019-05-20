import { parse } from 'query-string'
import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateToOfferAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'

const addAnchor = Selector('#add-stock')
const backButton = Selector('a.back-button')
const availableInput = Selector('input[name="available"]')
const closeManagerButton = Selector('#close-manager')
const manageStockAnchor = Selector('.manage-stock')
const submitButton = Selector('button.button.submitStep')
const priceInput = Selector('input[name="price"]')
const infoDiv = Selector('div.info')
const confirmationButton = infoDiv.find('button')

fixture('Initialisation')

let userRoleOne
let userRoleTwo
let userRoleThree
let userRoleFour
let userRoleFive
let dataFromSandboxOne
let dataFromSandboxTwo
let dataFromSandboxThree
let dataFromSandboxFour
let dataFromSandboxFive
test('Création des données', async () => {
  dataFromSandboxOne = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_no_stock'
  )
  userRoleOne = createUserRole(dataFromSandboxOne.user)

  dataFromSandboxTwo = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_stock'
  )
  userRoleTwo = createUserRole(dataFromSandboxTwo.user)

  dataFromSandboxThree = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_thing_offer_with_stock'
  )
  userRoleThree = createUserRole(dataFromSandboxThree.user)

  dataFromSandboxFour = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_no_iban_validated_user_offerer_with_thing_offer_with_no_stock'
  )
  userRoleFour = createUserRole(dataFromSandboxFour.user)

  dataFromSandboxFive = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_no_iban_validated_user_offerer_with_event_offer'
  )
  userRoleFive = createUserRole(dataFromSandboxFive.user)
})

fixture('Offer Gestion A | Créer des dates et des stocks')

test("Je peux créer un stock d'événement d'une offre vide sans remplir de champ", async t => {
  // given
  const { offer, user } = dataFromSandboxOne
  await navigateToOfferAs(user, offer, userRoleOne)(t)

  // when
  await t.click(manageStockAnchor).click(addAnchor)

  // then
  let location = await t.eval(() => window.location)
  let queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
  await t.expect(queryParams.stock).eql('creation')

  // when
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
  await t.expect(queryParams.stock).eql(undefined)
})

test('Je peux créer un autre stock et remplir des champs', async t => {
  // given
  const { offer, user } = dataFromSandboxOne
  await navigateToOfferAs(user, offer, userRoleOne)(t)

  // when
  await t.click(manageStockAnchor).click(addAnchor)

  // then
  let location = await t.eval(() => window.location)
  let queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
  await t.expect(queryParams.stock).eql('creation')

  // when
  await t.typeText(priceInput, '10').typeText(availableInput, '50')
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
  await t.expect(queryParams.stock).eql(undefined)
})

test('Je peux créer un stock en utilisant la touche Entrée', async t => {
  // given
  const { offer, user } = dataFromSandboxTwo
  await navigateToOfferAs(user, offer, userRoleTwo)(t)

  // when
  await t.click(manageStockAnchor).pressKey('Enter')

  // then
  let location = await t.eval(() => window.location)
  let queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
  await t.expect(queryParams.stock).eql('creation')

  // when
  await t.pressKey('Enter')

  // then
  location = await t.eval(() => window.location)
  queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
  await t.expect(queryParams.stock).eql(undefined)
})

test('Je peux fermer la fenêtre en utilisant la touche Escape', async t => {
  // given
  const { offer, user } = dataFromSandboxTwo
  await navigateToOfferAs(user, offer, userRoleTwo)(t)

  // when
  await t.click(manageStockAnchor).pressKey('esc')

  // then
  let location = await t.eval(() => window.location)
  const queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(undefined)
  await t.expect(queryParams.stock).eql(undefined)
})

test('Je peux fermer la fenêtre en cliquant sur le bouton Fermer', async t => {
  // given
  const scheduleCloseButton = Selector('button.button').withText('Fermer')
  const { offer, user } = dataFromSandboxTwo
  await navigateToOfferAs(user, offer, userRoleTwo)(t)

  // when
  await t.click(manageStockAnchor).click(scheduleCloseButton)

  // then
  let location = await t.eval(() => window.location)
  const queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(undefined)
})

test('Je peux interrompre la saisie en utilisant la touche Escape', async t => {
  // given
  const { offer, user } = dataFromSandboxTwo
  await navigateToOfferAs(user, offer, userRoleTwo)(t)

  // when
  await t.click(manageStockAnchor).pressKey('Enter')

  // then
  let location = await t.eval(() => window.location)
  let queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
  await t.expect(queryParams.stock).eql('creation')

  // when
  await t.pressKey('esc')

  // then
  location = await t.eval(() => window.location)
  queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
  await t.expect(queryParams.stock).eql(undefined)
})

test('Je ne peux pas rentrer un nouveau stock pour un objet avec déjà un stock', async t => {
  // given
  const { offer, user } = dataFromSandboxThree
  await navigateToOfferAs(user, offer, userRoleThree)(t)

  // when
  await t.click(manageStockAnchor)

  // then
  await t.expect(addAnchor.visible).notOk()
})

fixture('Offer Gestion B | Avertissement pour les offres sans iban')

test("J'ai une info quand je rentre un prix non nul pour l'objet d'une structure et un lieu sans iban", async t => {
  // given
  const { offer, user } = dataFromSandboxFour
  await navigateToOfferAs(user, offer, userRoleFour)(t)
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
  const queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
})

test("J'ai une info quand je rentre un prix non nul pour l'évènement d'une structure et un lieu sans iban", async t => {
  // given
  const { offer, user } = dataFromSandboxFive
  await navigateToOfferAs(user, offer, userRoleFive)(t)
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
  const queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
})

fixture('Offer Gestion C | Modifier des stocks')

test('Je peux modifier un stock', async t => {
  // given
  const beginInput = Selector('input.date')
  const datePicker = Selector('.react-datepicker')
  const datePickerLastDay = Selector(
    '.react-datepicker__week:last-child .react-datepicker__day:last-child'
  )
  const { offer, stock, user } = dataFromSandboxTwo
  const editAnchor = Selector(`#edit-stock-${stock.id}-button`)
  await navigateToOfferAs(user, offer, userRoleTwo)(t)
  await t.click(manageStockAnchor)

  // when
  await t.click(editAnchor)

  // then
  let location = await t.eval(() => window.location)
  let queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
  await t.expect(queryParams[`stock${stock.id}`]).eql('modification')
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
  await t.typeText(priceInput, '15')

  // when
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  queryParams = parse(location.search)
  await t.expect(queryParams.gestion).eql(null)
  await t.expect(queryParams.stock).eql(undefined)
})

test('Je peux aller sur le stock manager et revenir aux offres pour chercher une nouvelle offre sans bug de modal en appuyant sur Enter', async t => {
  // given
  const { offer, user } = dataFromSandboxTwo
  await navigateToOfferAs(user, offer, userRoleTwo)(t)
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

fixture.skip('TODO: Offer Gestion D | Effacer des dates et des stocks')

test('Je peux effacer un stock', async t => {
  const { offer, user } = dataFromSandboxTwo
  await navigateToOfferAs(user, offer, userRoleTwo)(t)
})
