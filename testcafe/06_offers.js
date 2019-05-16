import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateToOfferAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'

let dataFromSandbox
let userRole
fixture('Offers A | Lister les offres').beforeEach(async t => {
  if (!dataFromSandbox) {
    dataFromSandbox = await fetchSandbox(
      'pro_06_offers',
      'get_existing_pro_validated_user_with_at_least_one_visible_activated_offer'
    )
    userRole = createUserRole(dataFromSandbox.user)
  }
})

test("Lorsque je clique sur `Mes offres`, j'accède à la liste des offres", async t => {
  // given
  await t.useRole(userRole)
  const offerItem = Selector('li.offer-item')

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
  await t.expect(offerItem.count).gt(0)
})

test('Je peux désactiver ou activer une offre', async t => {
  // given
  const { offer } = dataFromSandbox
  const searchInput = Selector('#search')
  const submitButton = Selector('button[type="submit"]')
  // NOTE: pay attention that searching the offer here
  // is sufficient to find it in the list
  // (without needing of scrolling more)
  // otherwise offerActivSwitchButton will not be found
  const offerActiveSwitchButton = Selector('li.offer-item')
    .find(`a[href^="/offres/${offer.id}"]`)
    .parent('li.offer-item')
    .find('button.activ-switch')
  await t.useRole(userRole)
  await t.typeText(searchInput, offer.keywordsString).click(submitButton)

  // when
  await t.click(offerActiveSwitchButton)

  // then
  await t.expect(offerActiveSwitchButton.innerText).eql('Activer')

  // when
  await t.click(offerActiveSwitchButton)

  // then
  await t.expect(offerActiveSwitchButton.innerText).eql('Désactiver')
})

test('Je peux chercher une offre et aller sur sa page', async t => {
  // when
  const { offer, user } = dataFromSandbox
  await navigateToOfferAs(user, offer, userRole)(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/offres\/([A-Z0-9]*)/)
})
