import { ClientFunction, Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

import distanceOptions from '../src/helpers/search/distanceOptions'

const distanceOption = Selector('#filter-by-distance option')

const getPageUrl = ClientFunction(() => window.location.href.toString())

const filterButton = Selector('#filter-button')
const toogleFilterButton = Selector('#search-filter-menu-toggle-button').find(
  'img'
)

fixture(
  '05_05_01 Recherche par distance | Je me suis connecté·e | Je ne suis pas géolocalisé·e'
).beforeEach(async t => {
  const { user } = await fetchSandbox(
    'webapp_05_search',
    'get_existing_webapp_validated_user'
  )
  await t.useRole(createUserRole(user)).navigateTo(`${ROOT_PATH}recherche`)
  const location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/recherche')
    // ouverture du filtre
    .click(toogleFilterButton)
})

test('Je vois le titre de la recherche par distance', async t => {
  const title = Selector('#filter-by-distance').find('h2')
  await t.expect(title.innerText).eql('OÙ')
})

test('Par défaut, le selecteur est Toutes distances', async t => {
  await t.expect(
    distanceOption.withText(distanceOptions[0].label).hasAttribute('selected')
      .ok
  )
})

test('Je ne sélectionne aucun filtre et je clique sur filtrer', async t => {
  await t.click(filterButton)
  await t
    .expect(getPageUrl())
    .contains(`${ROOT_PATH}recherche/resultats`, { timeout: 2000 })
})

test('Je sélectionne toutes distances et je clique sur filtrer', async t => {
  const distanceInput = Selector('#filter-by-distance')
  await t
    .click(distanceInput)
    .click(distanceOption.withText(distanceOptions[0].label))
    .expect(distanceOption.withText(distanceOptions[0].label).value)
    .eql('20000')
    .click(filterButton)
    .expect(getPageUrl())
    .contains(`${ROOT_PATH}recherche/resultats`, {
      timeout: 2000,
    })
})

test('Je sélectionne toutes distances et je clique sur filtrer', async t => {
  const distanceInput = Selector('#filter-by-distance')
  await t
    .click(distanceInput)
    .click(distanceOption.withText(distanceOptions[1].label))
    .click(distanceInput)
    .click(distanceOption.withText(distanceOptions[0].label))
    .click(filterButton)
    .expect(getPageUrl())
    .contains(`${ROOT_PATH}recherche/resultats?distance=20000`, {
      timeout: 2000,
    })
})

test("Je sélectionne moins d'un km et je clique sur filtrer", async t => {
  const distanceInput = Selector('#filter-by-distance')
  await t
    .click(distanceInput)
    .click(distanceOption.withText(distanceOptions[1].label))
    .click(filterButton)
    .expect(getPageUrl())
    .contains(`${ROOT_PATH}recherche/resultats?distance=1`, { timeout: 2000 })
})

test('Je sélectionne moins de 10 kms et je clique sur filtrer', async t => {
  const distanceInput = Selector('#filter-by-distance')
  await t
    .click(distanceInput)
    .click(distanceOption.withText(distanceOptions[2].label))
    .click(filterButton)
    .expect(getPageUrl())
    .contains(`${ROOT_PATH}recherche/resultats?distance=10`, {
      timeout: 2000,
    })
})

test('Je sélectionne moins de 50 kms et je clique sur filtrer', async t => {
  const distanceInput = Selector('#filter-by-distance')
  await t
    .click(distanceInput)
    .click(distanceOption.withText(distanceOptions[3].label))
    .click(filterButton)
    .expect(getPageUrl())
    .contains(`${ROOT_PATH}recherche/resultats?distance=50`, {
      timeout: 2000,
    })
})
test('Je fais une recherche, je retourne sur la home, je réouvre la fenêtre de recherche, le filtre par distance est réinitialisé avec la valeur par défaut', async t => {
  const distanceInput = Selector('#filter-by-distance')
  await t
    .click(distanceInput)
    .click(distanceOption.withText(distanceOptions[2].label))
    .click(filterButton)
    .expect(getPageUrl())
    .contains(`${ROOT_PATH}recherche/resultats?distance=10`, {
      timeout: 2000,
    })

    .click(Selector('button.back-button'))
    .expect(getPageUrl())
    .contains(`${ROOT_PATH}recherche`, {
      timeout: 2000,
    })
    .click(toogleFilterButton)
    .expect(distanceOption.innerText)
    .eql('Toutes distances')
})
