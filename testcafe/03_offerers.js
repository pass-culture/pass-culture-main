import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import {
  navigateToOffererAs,
  navigateToOfferersAs,
} from './helpers/navigations'

const arrow = Selector('.caret a')
const firstArrow = arrow.nth(0)
const subTitleHeader = Selector('h2')

fixture(`OfferersPage A | Voir la liste de mes structures`)

test("L'utilisateur a au moins une structure validé, on peut aller dessus", async t => {
  // given
  const { offerer, user } = await fetchSandbox(
    'pro_03_offerers',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer'
  )
  const { id: offererId } = offerer

  // when
  await navigateToOfferersAs(user)(t)

  // then
  const activationOffererItem = Selector('.offerer-item')
    .find(`a[href="/structures/${offererId}"]`)
    .parent('.offerer-item')
  await t.expect(activationOffererItem.exists).ok()

  // when
  await t.click(firstArrow)

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

  // when
  await navigateToOfferersAs(user)(t)

  // then
  const activationOffererItemValidation = Selector('.offerer-item')
    .find(`a[href="/structures/${offererId}"]`)
    .parent('.offerer-item')
    .find('#offerer-item-validation')
  await t.expect(activationOffererItemValidation.exists).ok()

  // when
  await t.click(firstArrow)

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

  // when
  await navigateToOfferersAs(user)(t)

  // then
  const pendingOffererItem = Selector('.offerer-item.pending').withText(
    offererName
  )
  await t.expect(pendingOffererItem.exists).ok()

  // when
  await t.expect(firstArrow.exists).notOk()
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
