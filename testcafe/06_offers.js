import { Selector } from 'testcafe'

import { navigateToOfferAs } from './helpers/navigations'
import { EXISTING_EVENT_OFFER_WITH_NO_EVENT_OCCURRENCE_WITH_NO_STOCK_WITH_NO_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN } from './helpers/offers'
import { createUserRole } from './helpers/roles'
import { EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER } from './helpers/users'

async function trimed(selector, lol) {
  return await selector.innerText.then(value => value.trim())
}

const offerActivSwitchText = () => trimed(Selector('.offer-item .activ-switch'))

fixture`OffersList A | Lister les offres`

test("Lorsque je cliques sur `Mes offres`, j'accès de à la liste des offres", async t => {
  // given
  await t
    .useRole(createUserRole(EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER))
    .wait(1000)
  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
  await t.expect(await offerActivSwitchText()).eql('Désactiver')
})

test('Je peux désactiver ou activer des offres', async t => {
  // given
  const offerActivSwitch = Selector('.offer-item .activ-switch')
  await t.useRole(
    createUserRole(EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER)
  )

  // when
  await t.click(offerActivSwitch)

  // then
  await t.expect(await offerActivSwitchText()).eql('Activer')

  // when
  await t.click(offerActivSwitch)

  // then
  await t.expect(await offerActivSwitchText()).eql('Désactiver')
})

test('Je peux chercher une offre et aller sur sa page', async t => {
  // when
  await navigateToOfferAs(
    EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER,
    EXISTING_EVENT_OFFER_WITH_NO_EVENT_OCCURRENCE_WITH_NO_STOCK_WITH_NO_MEDIATION_WITH_93_OFFERER_IBAN_WITH_NO_VENUE_IBAN
  )(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/offres\/([A-Z0-9]*)/)
})
