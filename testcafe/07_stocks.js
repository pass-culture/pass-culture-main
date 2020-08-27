import { parse } from 'query-string'
import { Selector } from 'testcafe'

import { getUrlParams } from './helpers/location'
import { navigateToOfferAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'

const addAnchor = Selector('#add-stock')
const manageStockAnchor = Selector('.manage-stock')
const submitButton = Selector('button.button.submitStep')
const priceInput = Selector('input[name="price"]')
const addStockButton = Selector('#add-stock')
const stockItem = Selector('.stock-item')

fixture('En étant sur la page de détail d’une offre,')

test('Je peux créer un stock pour un événement', async t => {
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_no_stock'
  )
  const bookingLimitDatetime = Selector('#bookingLimitDatetime')
  const datePickerLastDay = Selector('.react-datepicker__day--today')
  await navigateToOfferAs(user, offer, createUserRole(user))(t)

  await t
    .click(manageStockAnchor)
    .click(addStockButton)

  let queryParams = parse(await getUrlParams())

  await t
    .expect(queryParams.stock)
    .eql('creation')
    .click(bookingLimitDatetime)
    .click(datePickerLastDay)
    .click(submitButton)

  queryParams = parse(await getUrlParams())
  await t
    .expect(queryParams.stock)
    .eql(undefined)
    .expect(stockItem.count)
    .eql(1)
})

test('Je ne peux pas créer un nouveau stock pour un objet ayant déjà un stock', async t => {
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_thing_offer_with_stock'
  )
  await navigateToOfferAs(user, offer, createUserRole(user))(t)

  await t
    .click(manageStockAnchor)
    .expect(addAnchor.visible)
    .notOk()
})

test('Je peux modifier un stock pour un événement', async t => {
  const { offer, stock, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_stock'
  )
  const beginInput = Selector('input.date')
  const datePicker = Selector('.react-datepicker')
  const datePickerLastDay = Selector('.react-datepicker__week:last-child .react-datepicker__day:last-child')
  const editAnchor = Selector(`#edit-stock-${stock.id}-button`)
  await navigateToOfferAs(user, offer, createUserRole(user))(t)

  await t
    .click(manageStockAnchor)
    .click(editAnchor)

  let queryParams = parse(await getUrlParams())
  await t
    .expect(queryParams.gestion)
    .eql(null)
    .expect(queryParams[`stock${stock.id}`])
    .eql('modification')
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
    .typeText(priceInput, '15')
    .click(submitButton)

  queryParams = parse(await getUrlParams())
  await t
    .expect(queryParams.gestion)
    .eql(null)
    .expect(queryParams.stock)
    .eql(undefined)
})

test('Je peux supprimer un stock pour un événement', async t => {
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_stock'
  )
  await navigateToOfferAs(user, offer, createUserRole(user))(t)
  const beginInput = Selector('input.date')
  const datePicker = Selector('.react-datepicker')
  const deleteButton = Selector('button.delete-stock')
  const deleteButtonConfirmation = Selector('button').withText('Oui')

  await t
    .click(manageStockAnchor)
    .click(deleteButton)
    .click(deleteButtonConfirmation)

  const queryParams = parse(await getUrlParams())
  await t
    .expect(queryParams.gestion)
    .eql(null)
    .expect(beginInput.exists)
    .notOk()
    .expect(datePicker.exists)
    .notOk()
    .expect(queryParams.stock)
    .eql(undefined)
})
