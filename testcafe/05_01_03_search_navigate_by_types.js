import { Selector } from 'testcafe'

import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import createUserRoleFromUserSandbox from './helpers/createUserRoleFromUserSandbox'

const searchUrl = `${ROOT_PATH}recherche`
let userRole

fixture(
  "O5_01_03 Recherche | Je cherche des offres par catégories et j'ai des résultats"
).beforeEach(async t => {
  if (!userRole) {
    userRole = await createUserRoleFromUserSandbox(
      'webapp_05_search',
      'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
    )
  }

  await t.useRole(userRole).navigateTo(searchUrl)
})

test("Je clique sur la vignette 'Lire' et je suis redirigé vers la page de résultats de la recherche, puis je clique sur la première offre et je regarde si le titre correspond", async t => {
  const buttonNavByOfferType = Selector('button').withText('Lire')

  await t
    .click(buttonNavByOfferType)
    .expect(getPageUrl())
    .contains('/recherche/resultats/Lire')

  const resultsForLireCategory = Selector('.search-results')
  const firstResultTitle = await resultsForLireCategory.find('h5').nth(0)
    .textContent
  const firstResultLink = resultsForLireCategory.find('.to-details').nth(0)

  await t
    .expect(resultsForLireCategory.exists)
    .ok()
    .click(firstResultLink)
    .expect(getPageUrl())
    .contains('/item')

  const offerDetailsTitle = Selector('#verso-offer-name').textContent

  await t.expect(offerDetailsTitle).eql(firstResultTitle)
})

test.skip("Je suis sur la page 'Lire', je clique sur le bouton de retour et j'arrive sur la page des catégories", async t => {
  const buttonNavByOfferType = Selector('button').withText('Lire')

  await t
    .click(buttonNavByOfferType)
    .expect(getPageUrl())
    .contains('/recherche/resultats/Lire')

  const backButton = Selector('.back-link')

  await t
    .expect(backButton.exists)
    .ok()
    .click(backButton)
    .expect(getPageUrl())
    .eql(searchUrl)
})
