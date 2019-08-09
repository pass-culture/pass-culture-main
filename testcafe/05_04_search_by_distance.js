import { ClientFunction, Selector } from 'testcafe'
import { ROOT_PATH } from '../src/utils/config'

import { distanceOptions } from '../src/components/pages/search/FilterControls/helpers'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

const getPageUrl = ClientFunction(() => window.location.href.toString())
const distanceInput = Selector('#filter-by-distance select')
const distanceOption = distanceInput.find('option')
const filterButton = Selector('#filter-button')
const toogleFilterButton = Selector('#search-filter-menu-toggle-button').find('img')

let userRole

fixture(
  '05_04_01 Recherche par distance | Je me suis connecté·e | Je ne suis pas géolocalisé·e'
).beforeEach(async t => {
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_05_search',
      'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
    )
  }

  await t.useRole(userRole).navigateTo(`${ROOT_PATH}recherche`)

  const location = await t.eval(() => window.location)

  await t
    .expect(location.pathname)
    .eql('/recherche')
    .click(toogleFilterButton)
})

test('Je sélectionne moins de 50 kms et je clique sur filtrer', async t => {
  await t
    .click(distanceInput)
    .click(distanceOption.withText(distanceOptions[3].label))
    .click(filterButton)
    .expect(getPageUrl())
    .contains(`${ROOT_PATH}recherche/resultats/tout?distance=50`)
})
