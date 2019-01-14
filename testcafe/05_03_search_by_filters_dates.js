import { ClientFunction, Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { youngUserRole } from './helpers/roles'

const getPageUrl = ClientFunction(() => window.location.href.toString())

const filterButton = Selector('#filter-button')
const resetButton = Selector('#search-filter-reset-button')

fixture(
  "O5_03_01 Recherche par Filtres | Je suis connecté·e | J'arrive sur la page de recherche | Icone open/close"
).beforeEach(async t => {
  await t.useRole(youngUserRole).navigateTo(`${ROOT_PATH}recherche`)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/recherche')
})

const toogleFilterButton = Selector('#search-filter-menu-toggle-button').find(
  'img'
)
const searchFilterMenu = Selector('#search-filter-menu')

test("Le filtre de recherche existe et l'icône n'est pas activé", async t => {
  await t
    .expect(toogleFilterButton.getAttribute('src'))
    .contains('ico-filter.svg')
})

test("Je peux ouvrir et fermer le filtre en cliquant sur l'icône", async t => {
  const classFilterDiv = searchFilterMenu.classNames
  await t

    // ouverture du filtre
    .click(toogleFilterButton)

    .expect(classFilterDiv)
    .contains('transition-status-entered')

    // changement de l'icône
    .expect(toogleFilterButton.getAttribute('src'))
    .contains('ico-chevron-up')

    // fermeture du filtre
    .click(toogleFilterButton)

    .expect(toogleFilterButton.getAttribute('src'))
    .contains('ico-filter.svg')

    .expect(classFilterDiv)
    .contains('transition-status-exited')
})

fixture('O5_03_02 Recherche par Filtres | Dates').beforeEach(async t => {
  await t
    .useRole(youngUserRole)
    .navigateTo(`${ROOT_PATH}recherche`)
    .click(toogleFilterButton)
})

const filterbyDatesDiv = Selector('#filter-by-dates')
const filterbyDatesTitle = filterbyDatesDiv.find('h2')

const checkboxDate1 = filterbyDatesDiv.find('input').nth(0)
const checkboxDate2 = filterbyDatesDiv.find('input').nth(1)
const checkboxDate3 = filterbyDatesDiv.find('input').nth(2)
const datePicker = filterbyDatesDiv.find('input').nth(3)

const utcExampleDay = Selector('.react-datepicker__week').withText('18')
const resetDatePickerInput = Selector('.react-datepicker__close-icon')

test('Je vois le titre de la section', async t => {
  await t
    .expect(filterbyDatesTitle.innerText)
    .eql('QUAND')
    .expect(datePicker.value)
    .eql('')
})

test('Je peux choisir entre 4 types de dates', async t => {
  const dateCheckboxes = filterbyDatesDiv.find('input')
  await t.expect(dateCheckboxes.count).eql(4)
})

test('Je ne sélectionne aucun filtre et je clique sur filtrer', async t => {
  await t.click(filterButton)
  await t
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}recherche/resultats`, { timeout: 2000 })
})

test('Quand on choisit un range de date après une date précise, le date picker est réinitialisé', async t => {
  await t
    .click(checkboxDate1)
    .wait(200)
    .click(datePicker)
    .wait(500)

    .click(utcExampleDay)

    // la valeur de l'input est mise à jour
    .expect(datePicker.value)
    .contains('17/')

    .click(checkboxDate1)

    // la valeur de l'input est réinitialisée
    .expect(datePicker.value)
    .contains('')
})

test('Je sélectionne les checkboxes par range de date', async t => {
  await t
    // Je séléctionne la première option
    .click(checkboxDate1)

    .expect(checkboxDate1.checked)
    .ok()
    .expect(checkboxDate2.checked)
    .notOk()
    .expect(checkboxDate3.checked)
    .notOk()

    .click(filterButton)

  await t
    .expect(getPageUrl())
    .contains(`&jours=0-1`, { timeout: 2000 })

    // Je coche toutes les options
    .wait(200)

    .click(checkboxDate2)
    .click(checkboxDate3)

    .wait(100)

    .expect(checkboxDate1.checked)
    .ok()
    .expect(checkboxDate2.checked)
    .ok()
    .expect(checkboxDate3.checked)
    .ok()

    .click(filterButton)

  await t
    .expect(getPageUrl())
    .contains(`&jours=0-1%2C1-5%2C5-100000`, { timeout: 2000 })
})

test('Je sélectionne plusieurs date, je filtre puis je clique sur réinitialiser', async t => {
  await t
    // Je coche toutes les options
    .click(checkboxDate1)
    .click(checkboxDate2)
    .click(checkboxDate3)

    .wait(200)

    .click(filterButton)

    .wait(200)

    // NB : On ne peut réinitialiser qu'après avoir fait un filtrage
    .click(resetButton)

    .wait(200)
    .expect(checkboxDate1.checked)
    .notOk()
    .expect(checkboxDate2.checked)
    .notOk()
    .expect(checkboxDate3.checked)
    .notOk()

  await t
    .expect(getPageUrl())
    .contains(`/recherche/resultats?page=`, { timeout: 2000 })
})

test("Je sélectionne plusieurs date puis j'utilise le date picker", async t => {
  await t
    // Je coche toutes les options
    .click(checkboxDate1)
    .click(checkboxDate2)
    .click(checkboxDate3)

    .click(datePicker)

    .wait(200)

    // Je sélectionne une date via le date picker
    .click(utcExampleDay)

    .expect(checkboxDate1.checked)
    .notOk()
    .expect(checkboxDate2.checked)
    .notOk()
    .expect(checkboxDate3.checked)
    .notOk()

    .expect(datePicker.value)
    .contains('17/')

    .click(filterButton)

  // await t.expect(getPageUrl()).contains('-16')
  // FIXME UTC sur Circle CI différente que sur l'app
  await t.expect(getPageUrl()).contains('/recherche/resultats?date=')
})
test('Je peux réinitiliaser la date choisie via le date picker', async t => {
  await t
    // Je coche toutes les options
    .click(checkboxDate1)

    .click(datePicker)

    .wait(200)

    // Je sélectionne une date via le date picker
    .click(utcExampleDay)

    .expect(datePicker.value)
    .contains('17/')

    .click(resetDatePickerInput)

    .expect(datePicker.value)
    .eql('')
})

fixture('O5_03_02 Recherche par Filtres | Distance ').beforeEach(async t => {
  await t
    .useRole(youngUserRole)
    .navigateTo(`${ROOT_PATH}recherche`)
    .click(toogleFilterButton)
})

const filterbyDistanceDiv = Selector('#filter-by-distance')
const filterbyDistanceTitle = filterbyDistanceDiv.find('h2')

test('Je vois le titre de la section', async t => {
  await t.expect(filterbyDistanceTitle.innerText).eql('OÙ')
})

fixture(
  "O5_03_02 Recherche par Filtres | Par Type d'offres / Catégories"
).beforeEach(async t => {
  await t
    .useRole(youngUserRole)
    .navigateTo(`${ROOT_PATH}recherche`)
    .click(toogleFilterButton)
})

const filterbyOfferTypesDiv = Selector('#filter-by-offer-types')
const filterbyOfferTypesTitle = filterbyOfferTypesDiv.find('h2')

test('Je vois le titre de la section', async t => {
  await t.expect(filterbyOfferTypesTitle.innerText).eql('QUOI')
})
