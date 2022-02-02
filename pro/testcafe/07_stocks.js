import { Selector } from 'testcafe'

import { navigateToOfferAs, navigateToStocksAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'

const addThingStockButton = Selector('button').withText('Ajouter un stock')
const addEventStockButton = Selector('button').withText('Ajouter une date')
const submitButton = Selector('button').withText('Enregistrer')
const priceInput = Selector('input[name="price"]')
const stockItem = Selector('tbody').find('tr')
const submitSuccess = Selector('.notification.is-success').withText(
  'Vos stocks ont bien été sauvegardés.'
)

fixture('En étant sur la page des stocks d’une offre,')

test("Je peux créer un stock pour un événement en passant par la page de l'offre", async t => {
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_no_stock'
  )
  const stocksAnchor = Selector(
    `a[href^="/offre/${offer.id}/individuel/stocks"]`
  ).withText('Stock et prix')

  const dateInput = Selector('.react-datepicker-wrapper').nth(0)
  const hourInput = Selector('.react-datepicker-wrapper').nth(1)
  const datePickerLastDay = Selector(
    '.react-datepicker__week:last-child .react-datepicker__day:last-child'
  )
  const hourPickerLastHour = Selector(
    '.react-datepicker__time-list-item:last-child'
  )
  await navigateToOfferAs(user, offer, createUserRole(user))(t)

  await t.click(stocksAnchor).click(addEventStockButton)

  await t
    .click(dateInput)
    .click(datePickerLastDay)
    .click(hourInput)
    .click(hourPickerLastHour)
    .typeText(priceInput, '15')
    .click(submitButton)

  await t.expect(submitSuccess.exists).ok().expect(stockItem.count).eql(1)
})

test('Je ne peux pas créer un nouveau stock pour un objet ayant déjà un stock en passant par la page des offres', async t => {
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_thing_offer_with_stock'
  )
  await navigateToStocksAs(user, offer, createUserRole(user))(t)

  await t.expect(addThingStockButton.exists).notOk({ timeout: 200 })
})

test('Je peux modifier un stock pour un événement', async t => {
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_stock'
  )

  const dateInput = Selector('.react-datepicker-wrapper').nth(0)
  const hourInput = Selector('.react-datepicker-wrapper').nth(1)
  const datePickerPopin = Selector('.react-datepicker')
  const datePickerLastDay = Selector(
    '.react-datepicker__week:last-child .react-datepicker__day:last-child'
  )
  const hourPickerLastHour = Selector(
    '.react-datepicker__time-list-item:last-child'
  )
  await navigateToStocksAs(user, offer, createUserRole(user))(t)

  await t
    .expect(dateInput.exists)
    .ok()
    .expect(datePickerPopin.exists)
    .notOk()
    .click(dateInput)
    .expect(datePickerPopin.exists)
    .ok()
    .click(datePickerLastDay)
    .expect(datePickerPopin.exists)
    .notOk()
    .expect(hourInput.exists)
    .ok()
    .expect(datePickerPopin.exists)
    .notOk()
    .click(hourInput)
    .expect(datePickerPopin.exists)
    .ok()
    .click(hourPickerLastHour)
    .expect(datePickerPopin.exists)
    .notOk()
    .typeText(priceInput, '15')
    .click(submitButton)

  await t
    .expect(submitSuccess.exists)
    .ok()
    .expect(priceInput.value)
    .contains('15')
    .expect(stockItem.count)
    .eql(1)
})

test('Je peux supprimer un stock pour un événement', async t => {
  const { offer, user } = await fetchSandbox(
    'pro_08_stocks',
    'get_existing_pro_validated_user_with_validated_offerer_with_iban_validated_user_offerer_with_event_offer_with_stock'
  )
  await navigateToStocksAs(user, offer, createUserRole(user))(t)
  const deleteButton = Selector('td').find('button')
  const deleteButtonConfirmation = Selector('.action-buttons')
    .find('button')
    .withText('Supprimer')
  const deleteSuccess = Selector('.notification.is-success').withText(
    'Le stock a été supprimé.'
  )

  await t
    .click(deleteButton)
    .click(Selector('div[title="Supprimer le stock"]'))
    .expect(deleteButtonConfirmation.exists)
    .ok()
    .click(deleteButtonConfirmation)
    .expect(deleteSuccess.exists)
    .ok()
    .expect(stockItem.count)
    .eql(0)
})
