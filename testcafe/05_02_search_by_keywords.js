import { Selector } from 'testcafe'

import getPageUrl from './helpers/getPageUrl'
import { createUserRole } from './helpers/roles'
import { hasSignedUpUser93 } from './helpers/users'
import { ROOT_PATH } from '../src/utils/config'

const searchInput = Selector('#keywords')
const keywordsSearchButton = Selector('#keywords-search-button')

const resultsTitle = Selector('#results-title')
const baseUrl = `${ROOT_PATH}recherche`
fixture("O5_02_01 Recherche | J'effectue une recherche par mot-clé").beforeEach(
  async t => {
    await t.useRole(createUserRole(hasSignedUpUser93)).navigateTo(baseUrl)
  }
)

test("Je fais une recherche par mots-clés et je n'ai pas de résultats", async t => {
  // given
  const keyword = 'fake'
  const resultUrl = `${baseUrl}/resultats?mots-cles=${keyword}`

  // then
  await t
    .wait(500)
    .typeText(searchInput, keyword)
    .click(keywordsSearchButton)
    .wait(500)

  await t.expect(getPageUrl()).eql(resultUrl)
  await t.expect(resultsTitle.innerText).eql('"FAKE" : 0 RÉSULTAT')
})

test("Je fais une recherche par mots-clés et j'ai plusieurs résultats", async t => {
  // given
  const keyword = 'ravage'
  const keywordUpper = keyword.toLocaleUpperCase()

  // then
  await t
    .typeText(searchInput, keyword)
    .click(keywordsSearchButton)
    .wait(500)
  const expected = `"${keywordUpper}" : 3 RÉSULTATS`
  await t.expect(resultsTitle.innerText).eql(expected)
})

test("Je fais une recherche par mots-clés et j'ai un seul résultat", async t => {
  // given
  const keyword = 'funky'
  const keywordUpper = keyword.toLocaleUpperCase()

  // then
  await t
    .typeText(searchInput, keyword)
    .click(keywordsSearchButton)
    .wait(500)
  const expected = `"${keywordUpper}" : 1 RÉSULTAT`
  await t.expect(resultsTitle.innerText).eql(expected)
})
