import { Selector } from 'testcafe'

import getPageUrl from './helpers/getPageUrl'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const searchInput = Selector('#keywords')
const keywordsSearchButton = Selector('#keywords-search-button')
const resultsTitle = Selector('#results-title')
const baseUrl = `${ROOT_PATH}recherche`

let userRole

fixture("O5_02_01 Recherche | J'effectue une recherche par mot-clé").beforeEach(async t => {
  if (!userRole) {
    const { user } = await fetchSandbox(
      'webapp_05_search',
      'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
    )
    userRole = createUserRole(user)
  }
  await t.useRole(userRole).navigateTo(baseUrl)
})

test("Je fais une recherche par mots-clés et je n'ai pas de résultats", async t => {
  // given
  const keyword = 'fake'
  const resultUrl = `${baseUrl}/resultats/tout?mots-cles=${keyword}`

  // when
  await t
    .wait(500)
    .typeText(searchInput, keyword)
    .click(keywordsSearchButton)
    .wait(500)

  // then
  await t.expect(getPageUrl()).eql(resultUrl)
  await t.expect(resultsTitle.innerText).eql('"FAKE" : 0 RÉSULTAT')
})

test("Je fais une recherche par mots-clés et j'ai plusieurs résultats", async t => {
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

test("Je fais une recherche par mots-clés et j'ai un seul résultat", async t => {
  // given
  const keyword = 'narval'
  const keywordUpper = keyword.toLocaleUpperCase()

  // when
  await t
    .typeText(searchInput, keyword)
    .click(keywordsSearchButton)
    .wait(500)

  // then
  const expected = `"${keywordUpper}" : 1 RÉSULTAT`
  await t.expect(resultsTitle.innerText).eql(expected)
})
