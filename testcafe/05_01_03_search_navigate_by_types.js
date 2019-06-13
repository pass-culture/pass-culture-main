import { Selector } from 'testcafe'

import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

let userRole

fixture(
  "O5_01_03 Recherche | Je cherche des offres par catégories et j'ai des résultats"
).beforeEach(async t => {
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_05_search',
      'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
    )

    await t.useRole(userRole).navigateTo(`${ROOT_PATH}recherche/`)
  }
})

test("Je clique sur la vignette 'Lire' et je suis redirigé vers la page de résultats de la recherche", async t => {
  const buttonNavByOfferType = Selector('button').withText('Lire')

  await t
    .click(buttonNavByOfferType)
    .expect(getPageUrl())
    .contains('/recherche/resultats/Lire')

  const resultsForLireCategory = Selector('.search-results')
  const firstResultTitle = resultsForLireCategory.find('h5').nth(0)
  const linkResult = resultsForLireCategory.find('.to-details')

  await t
    .expect(resultsForLireCategory.exists)
    .ok()
    .expect(resultsForLireCategory.find('h5').exists)
    .ok()
    .click(linkResult)

  await t.expect(getPageUrl()).contains('/item')

  const offerDetailsTitle = Selector('#verso-offer-name')

  await t
    .expect(offerDetailsTitle.textContent)
    .eql(firstResultTitle.textContent)
})

test('Depuis des résultats par catégorie, je peux revenir à la page des catégories', async t => {
  const buttonNavByOfferType = Selector('button').withText('Lire')

  await t
    .click(buttonNavByOfferType)
    .expect(getPageUrl())
    .contains('/recherche/resultats/Lire')

  const backButton = Selector('button.back-button')

  await t
    .expect(backButton.exists)
    .ok()
    .click(backButton)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}recherche`)
})
