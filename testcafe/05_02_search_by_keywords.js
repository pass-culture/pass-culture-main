import { Selector } from 'testcafe'

import getPageUrl from './helpers/getPageUrl'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const searchInput = Selector('#keywords')
const keywordsSearchButton = Selector('#keywords-search-button')
const resultsTitle = Selector('#results-title')
const baseUrl = `${ROOT_PATH}recherche`

fixture("O5_02_01 Recherche | J'effectue une recherche par mot-clé").beforeEach(
  async t => {
    const { user } = await fetchSandbox(
      'webapp_05_search',
      'get_existing_webapp_validated_user'
    )
    await t.useRole(createUserRole(user)).navigateTo(baseUrl)
  }
)

test("Je fais une recherche par mots-clés et je n'ai pas de résultats", async t => {
  // given
  const keyword = 'fake'
  const resultUrl = `${baseUrl}/resultats?mots-cles=${keyword}`

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
  const expected = `"${keywordUpper}" : 4 RÉSULTATS`
  await t.expect(resultsTitle.innerText).eql(expected)
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
