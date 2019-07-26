import { Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const searchInput = Selector('#keywords')
const keywordsSearchButton = Selector('#keywords-search-button')
const resultsTitle = Selector('#results-title')
const baseUrl = `${ROOT_PATH}recherche`

const searchItem = Selector('.recommendation-list-item')
const itemDetailsArrow = searchItem.find('.icon-legacy-next')
const versoOfferName = Selector('#verso-offer-name')

const backLink = Selector('.back-link')

let userRole

fixture('En étant sur la recherche,').beforeEach(async t => {
  if (!userRole) {
    const { user } = await fetchSandbox(
      'webapp_05_search',
      'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
    )
    userRole = createUserRole(user)
  }
  await t.useRole(userRole).navigateTo(baseUrl)
})

test("Je peux chercher une offre par titre (mot-clé) et j'obtiens des résultats", async t => {
  // given
  const keyword = 'ravage'
  const keywordUpper = keyword.toLocaleUpperCase()

  // when
  await t
    .typeText(searchInput, keyword)
    .click(keywordsSearchButton)
    .wait(500)

  // then
  const expected = new RegExp(`"${keywordUpper}" : [0-9] RÉSULTATS`)
  await t.expect(resultsTitle.innerText).match(expected)
})

test('Je peux cliquer sur une icône chevron pour accéder au détail', async t => {
  // given
  const keyword = 'ravage'

  // when
  await t
    .typeText(searchInput, keyword)
    .click(keywordsSearchButton)
    .wait(500)

  // then
  await t
    .expect(itemDetailsArrow.exists)
    .ok()
    .click(itemDetailsArrow)
    .wait(500)
    .expect(versoOfferName.exists)
    .ok()
})

test('Je peux revenir en arrière en cliquant sur le bouton retour', async t => {
  // given
  const keyword = 'ravage'

  // when
  await t
    .typeText(searchInput, keyword)
    .click(keywordsSearchButton)
    .wait(500)

  // then
  await t
    .expect(searchItem.exists)
    .ok()
    .expect(itemDetailsArrow.exists)
    .ok()
    .click(itemDetailsArrow)
    .wait(500)
    .expect(versoOfferName.exists)
    .ok()
    .expect(backLink.exists)
    .ok()
    .click(backLink)
    .expect(searchItem.exists)
})
