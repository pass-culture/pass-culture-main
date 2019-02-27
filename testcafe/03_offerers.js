import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import {
  navigateToOffererAs,
  navigateToOfferersAs,
} from './helpers/navigations'

const subTitleHeader = Selector('h2')

fixture(`OfferersPage A | Voir la liste de mes structures`)

test("L'utilisateur a au moins une structure validé, on peut aller dessus", async t => {
  // given
  const { offerer, user } = await fetchSandbox(
    'pro_03_offerers',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer'
  )
  const { id: offererId } = offerer
  const activationOffererItem = Selector('.offerer-item')
    .find(`a[href="/structures/${offererId}"]`)
    .parent('.offerer-item')
  const arrow = activationOffererItem.find('div.caret').find('a')

  // when
  await navigateToOfferersAs(user)(t)

  // then
  await t.expect(activationOffererItem.exists).ok()

  // when
  await t.click(arrow)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/structures\/([A-Z0-9]*)$/)
  await t.expect(subTitleHeader.exists).ok()
})

test("L'utilisateur a au moins une structure en cours de validation, mais on peut aller dessus", async t => {
  // given
  const { offerer, user } = await fetchSandbox(
    'pro_03_offerers',
    'get_existing_pro_validated_user_with_not_validated_offerer_validated_user_offerer'
  )
  const { id: offererId } = offerer
  const activationOffererItem = Selector('.offerer-item')
    .find(`a[href="/structures/${offererId}"]`)
    .parent('.offerer-item')
  const activationOffererItemValidation = activationOffererItem.find(
    '#offerer-item-validation'
  )
  const arrow = activationOffererItem.find('div.caret').find('a')

  // when
  await navigateToOfferersAs(user)(t)

  // then
  await t.expect(activationOffererItemValidation.exists).ok()

  // when
  await t.click(arrow)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/structures\/([A-Z0-9]*)$/)
  await t.expect(subTitleHeader.exists).ok()
})

test("L'utilisateur a au moins un rattachement à une structure en cours de validation, on ne peut pas aller dessus", async t => {
  // given
  const { offerer, user } = await fetchSandbox(
    'pro_03_offerers',
    'get_existing_pro_validated_user_with_validated_offerer_not_validated_user_offerer'
  )
  const { name: offererName } = offerer
  const pendingOffererItem = Selector('.offerer-item.pending').withText(
    offererName
  )
  const arrow = pendingOffererItem.find('div.caret').find('a')

  // when
  await navigateToOfferersAs(user)(t)

  // then
  await t.expect(pendingOffererItem.exists).ok()

  // when
  await t.expect(arrow.exists).notOk()
})

fixture('OfferersPage B | Recherche')

test('Je peux chercher une structure avec des mots-clés et naviguer sur sa page', async t => {
  // given
  const { offerer, user } = await fetchSandbox(
    'pro_03_offerers',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer'
  )
  await navigateToOffererAs(user, offerer)(t)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/structures\/([A-Z0-9]*)/)
})
