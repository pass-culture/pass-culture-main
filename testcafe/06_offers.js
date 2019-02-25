import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateToOfferAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'

async function trimed(selector, lol) {
  return await selector.innerText.then(value => value.trim())
}

const offerActivSwitchText = () => trimed(Selector('.offer-item .activ-switch'))

fixture('OffersList A | Lister les offres').beforeEach(async t => {
  t.ctx.sandbox = await fetchSandbox(
    'pro_06_offers',
    'get_existing_pro_validated_user_with_at_least_one_visible_activated_offer'
  )
})

test("Lorsque je cliques sur `Mes offres`, j'accès de à la liste des offres", async t => {
  // given
  const { user } = t.ctx.sandbox
  await t.useRole(createUserRole(user))
  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
  await t.expect(await offerActivSwitchText()).eql('Désactiver')
})

test('Je peux désactiver ou activer des offres', async t => {
  // given
  const { user } = t.ctx.sandbox
  const offerActivSwitch = Selector('.offer-item .activ-switch')
  await t.useRole(createUserRole(user))

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
  const { offer, user } = t.ctx.sandbox
  await navigateToOfferAs(user, offer)(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/offres\/([A-Z0-9]*)/)
})
