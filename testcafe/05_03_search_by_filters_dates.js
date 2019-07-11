import { Selector } from 'testcafe'

import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

const filterButton = Selector('#filter-button')
const resetButton = Selector('#search-filter-reset-button')
const toggleFilterButton = Selector('#search-filter-menu-toggle-button').find('img')
const searchFilterMenu = Selector('#search-filter-menu')
const filterByDatesDiv = Selector('#filter-by-dates')
const filterByDatesTitle = filterByDatesDiv.find('h2')
const checkboxDate1 = filterByDatesDiv.find('input').nth(0)
const checkboxDate2 = filterByDatesDiv.find('input').nth(1)
const checkboxDate3 = filterByDatesDiv.find('input').nth(2)
const datePicker = filterByDatesDiv.find('input').nth(3)
const utcExampleDay = Selector('.react-datepicker__day').withText('14')
const nextMonthButton = Selector('.react-datepicker__navigation--next')
const resetDatePickerInput = Selector('.react-datepicker__close-icon')
const filterByDistanceDiv = Selector('#filter-by-distance')
const filterByDistanceTitle = filterByDistanceDiv.find('h2')
const filterByOfferTypesDiv = Selector('#filter-by-offer-types')
const filterByOfferTypesTitle = filterByOfferTypesDiv.find('h2')

let userRole

fixture(
  "O5_03_01 Recherche par Filtres | Je suis connecté·e | J'arrive sur la page de recherche | Icone open/close"
).beforeEach(async t => {
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_05_search',
      'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
    )
  }

  await t.useRole(userRole).navigateTo(`${ROOT_PATH}recherche`)

  const location = await t.eval(() => window.location)

  await t.expect(location.pathname).eql('/recherche')
})

test("Le filtre de recherche existe et l'icône n'est pas activé", async t => {
  await t.expect(toggleFilterButton.getAttribute('src')).contains('ico-filter.svg')
})

test("Je peux ouvrir et fermer le filtre en cliquant sur l'icône", async t => {
  const classFilterDiv = searchFilterMenu.classNames

  await t
    .click(toggleFilterButton)
    .expect(classFilterDiv)
    .contains('transition-status-entered')
    .expect(toggleFilterButton.getAttribute('src'))
    .contains('ico-chevron-up')
    .click(toggleFilterButton)
    .expect(toggleFilterButton.getAttribute('src'))
    .contains('ico-filter.svg')
    .expect(classFilterDiv)
    .contains('transition-status-exited')
})

fixture('O5_03_02 Recherche par Filtres | Dates').beforeEach(async t => {
  await t
    .useRole(userRole)
    .navigateTo(`${ROOT_PATH}recherche`)
    .click(toggleFilterButton)
})

test('Je vois le titre de la section (QUAND)', async t => {
  await t
    .expect(filterByDatesTitle.innerText)
    .eql('QUAND')
    .expect(datePicker.value)
    .eql('')
})

test('Je peux choisir entre 4 types de dates', async t => {
  const dateCheckboxes = filterByDatesDiv.find('input')

  await t.expect(dateCheckboxes.count).eql(4)
})

test('Je ne sélectionne aucun filtre et je clique sur filtrer', async t => {
  await t.click(filterButton)
  await t.expect(getPageUrl()).eql(`${ROOT_PATH}recherche/resultats`)
})

test('Quand on choisit un range de date après une date précise, le date picker est réinitialisé', async t => {
  await t
    .click(checkboxDate1)
    .wait(200)
    .click(datePicker)
    .wait(500)
    .click(nextMonthButton)
    .click(utcExampleDay)
    .wait(500)

  await t
    .expect(datePicker.value)
    .contains('14/')
    .click(checkboxDate1)
    .expect(datePicker.value)
    .contains('')
})

// TODO: this is a not well understood test crashing sometimes because of mysterious wait
// This test is therefore skipped and has to be internalized inside jest tests.
test.skip('Je sélectionne les checkboxes par range de date', async t => {
  // when
  await t.click(checkboxDate1)

  // then
  await t
    .expect(checkboxDate1.checked)
    .ok()
    .expect(checkboxDate2.checked)
    .notOk()
    .expect(checkboxDate3.checked)
    .notOk()

  // when
  await t.click(filterButton)

  // then
  await t.expect(getPageUrl()).contains(`&jours=0-1`)

  // when
  await t.click(toggleFilterButton).wait(1000)
  await t.click(checkboxDate2).wait(200)
  await t.click(checkboxDate3).wait(200)

  // then
  await t
    .expect(checkboxDate1.checked)
    .ok()
    .expect(checkboxDate2.checked)
    .ok()
    .expect(checkboxDate3.checked)
    .ok()

  // when
  await t.click(filterButton)

  // then
  await t.expect(getPageUrl()).contains(`&jours=0-1%2C1-5%2C5-100000`)
})

test('Je sélectionne plusieurs dates, je filtre puis je clique sur réinitialiser', async t => {
  // when
  await t
    .click(checkboxDate1)
    .click(checkboxDate2)
    .click(checkboxDate3)
    .wait(200)
    .click(filterButton)
    .wait(200)
    .click(toggleFilterButton)
    .click(resetButton)
    .wait(200)

  // then
  await t
    .expect(checkboxDate1.checked)
    .notOk()
    .expect(checkboxDate2.checked)
    .notOk()
    .expect(checkboxDate3.checked)
    .notOk()

  await t.expect(getPageUrl()).contains(`/recherche/resultats`)
})

test("Je sélectionne plusieurs dates puis j'utilise le date picker", async t => {
  await t
    .click(checkboxDate1)
    .click(checkboxDate2)
    .click(checkboxDate3)
    .click(datePicker)
    .wait(200)
    .click(nextMonthButton)
    .click(utcExampleDay)
    .expect(checkboxDate1.checked)
    .notOk()
    .expect(checkboxDate2.checked)
    .notOk()
    .expect(checkboxDate3.checked)
    .notOk()
    .expect(datePicker.value)
    .contains('14/')
    .click(filterButton)

  await t.expect(getPageUrl()).contains('/recherche/resultats?date=')
})

test('Je peux réinitialiser la date choisie via le date picker', async t => {
  await t
    .click(checkboxDate1)
    .click(datePicker)
    .wait(200)
    .click(nextMonthButton)
    .click(utcExampleDay)
    .expect(datePicker.value)
    .contains('14/')
    .click(resetDatePickerInput)
    .expect(datePicker.value)
    .eql('')
})

fixture('O5_03_03 Recherche par Filtres | Distance ').beforeEach(async t => {
  await t
    .useRole(userRole)
    .navigateTo(`${ROOT_PATH}recherche`)
    .click(toggleFilterButton)
})

test('Je vois le titre de la section (OÙ)', async t => {
  await t.expect(filterByDistanceTitle.innerText).eql('OÙ')
})

fixture("O5_03_04 Recherche par Filtres | Par Type d'offres / Catégories").beforeEach(async t => {
  await t
    .useRole(userRole)
    .navigateTo(`${ROOT_PATH}recherche`)
    .click(toggleFilterButton)
})

test('Je vois le titre de la section (QUOI)', async t => {
  await t.expect(filterByOfferTypesTitle.innerText).eql('QUOI')
})
