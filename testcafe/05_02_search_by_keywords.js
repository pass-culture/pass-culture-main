import { Selector } from 'testcafe'

import { youngUserRole } from './helpers/roles'
import { ROOT_PATH } from '../src/utils/config'

const searchInput = Selector('#keywords')
const keywordsSearchButton = Selector('#keywords-search-button')

const resultsTitle = Selector('#results-title')

fixture("O5_02_01 Recherche | J'effectue une recherche par mot-clé").beforeEach(
  async t => {
    await t.useRole(youngUserRole).navigateTo(`${ROOT_PATH}recherche`)
  }
)

test("Je fais une recherche par mots-clés et je n'ai pas de résultats", async t => {
  await t
    .wait(500)
    .typeText(searchInput, 'fake')
    .click(keywordsSearchButton)
    .wait(500)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/recherche/resultats')
  await t.expect(resultsTitle.innerText).eql('"FAKE" : 0 RÉSULTAT')
})

test("Je fais une recherche par mots-clés et j'ai des résultats", async t => {
  await t
    .typeText(searchInput, 'lepage')
    .click(keywordsSearchButton)
    .wait(500)
  await t.expect(resultsTitle.innerText).eql('"LEPAGE" : 1 RÉSULTAT')
})
