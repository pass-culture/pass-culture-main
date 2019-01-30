import { Selector } from 'testcafe'

import {
  navigateToOffererAs,
  navigateToOfferersAs,
} from './helpers/navigations'
import { EXISTING_93_OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN } from './helpers/offerers'
import { EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER } from './helpers/users'

const activationMessage = Selector('#offerer-item-validation')
const arrow = Selector('.caret a')
const firstArrow = arrow.nth(0)
const subTitleHeader = Selector('h2')

fixture(`OfferersPage A | Voir la liste de mes structures`).beforeEach(
  // given
  navigateToOfferersAs(EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER)
)

test("La structure qui vient d'être créée est en attente de validation", async t => {
  // then
  await t
    .expect(activationMessage.innerText)
    .eql("Structure en cours de validation par l'équipe Pass Culture.")
})

test("Je peux voir les détails d'une structure", async t => {
  // when
  await t.click(firstArrow)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/structures\/([A-Z0-9]*)$/)
  await t.expect(subTitleHeader.exists).ok()
})

fixture`OfferersPage B | Recherche`

test('Je peux chercher une structure avec des mots-clés et naviguer sur sa page', async t => {
  // given
  await navigateToOffererAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_93_OFFERER_WITH_NO_PHYSICAL_VENUE_WITH_NO_IBAN
  )(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/structures\/([A-Z0-9]*)/)
})
