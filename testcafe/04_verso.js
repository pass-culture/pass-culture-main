/* eslint
  no-param-reassign: 0
*/
import { Selector } from 'testcafe'

import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import { getVersoWallet, getVersoWalletValue } from './helpers/getVersoWallet'
import { ROOT_PATH } from '../src/utils/config'

const thingBaseURL = 'KU/F4'
const discoverURL = `${ROOT_PATH}decouverte`
const offerPage = `${discoverURL}/${thingBaseURL}`

const versoOfferName = Selector('#verso-offer-name')
const versoOfferVenue = Selector('#verso-offer-venue')
const closeVersoButton = Selector('#deck-close-verso-button')
const openVersoButton = Selector('#deck-open-verso-button')

fixture(`04 Verso`).beforeEach(async t => {
  // given
  const { user } = await fetchSandbox(
    'webapp_04_verso',
    'get_existing_webapp_hbs_user'
  )
  await t.useRole(createUserRole(user)).navigateTo(offerPage)
})

test(`L'user doit pouvoir cliquer sur le bouton pour ouvrir le verso`, async t => {
  await t
    .wait(3000)
    .expect(openVersoButton.exists)
    .ok()
    .click(openVersoButton)
    .expect(closeVersoButton.exists)
    .ok()
})

test(`La somme affichée est supérieure à 0`, async t => {
  // when
  await t.click(openVersoButton).wait(500)
  // then
  const versoWallet = await getVersoWallet()
  const versoWalletValue = await getVersoWalletValue()
  await t.expect(versoWallet).contains('€')
  await t.expect(versoWalletValue).gte(0)
})

test('Le titre et le nom du lieu sont affichés', async t => {
  await t
    .click(openVersoButton)
    .expect(versoOfferName.textContent)
    .eql('Dormons peu soupons bien, de Eloise Jomenrency')
    .expect(versoOfferVenue.textContent)
    .eql('Cinéma de la fin (Offre en ligne)')
})

fixture(`04 Verso, quand l'user n'a plus d'argent`).beforeEach(async t => {
  // given
  const { user } = await fetchSandbox(
    'webapp_04_verso',
    'get_existing_webapp_hnmm_user'
  )
  await t.useRole(createUserRole(user)).navigateTo(offerPage)
})

test(`La somme affichée est égale à 0`, async t => {
  // when
  await t.click(openVersoButton).wait(500)
  const versoWallet = await getVersoWallet()
  const versoWalletValue = await getVersoWalletValue()
  // then
  await t.expect(versoWallet).contains('€')
  await t.expect(versoWalletValue).eql(0)
})
