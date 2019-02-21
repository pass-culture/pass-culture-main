// $(yarn bin)/testcafe chrome ./testcafe/04_verso.js
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

const openVerso = Selector('#deck-open-verso-button')

fixture(`04_01 Verso, montant du porte-monnaie`)

test(`La somme affichée est égale à 0`, async t => {
  // given
  const { user } = await fetchSandbox(
    'webapp_04_verso',
    'get_existing_webapp_hnmm_user'
  )
  // when
  await t
    .useRole(createUserRole(user))
    .navigateTo(offerPage)
    .click(openVerso)
  const versoWallet = await getVersoWallet()
  const versoWalletValue = await getVersoWalletValue()
  // then
  await t.expect(versoWallet).contains('€')
  await t.expect(versoWalletValue).eql(0)
})

test(`La somme affichée est supérieure à 0`, async t => {
  // given
  const { user } = await fetchSandbox(
    'webapp_04_verso',
    'get_existing_webapp_hbs_user'
  )
  await t
    .useRole(createUserRole(user))
    .navigateTo(offerPage)
    .click(openVerso)
  // when
  const versoWallet = await getVersoWallet()
  const versoWalletValue = await getVersoWalletValue()
  // then
  await t.expect(versoWallet).contains('€')
  await t.expect(versoWalletValue).gte(0)
})

// fixture(`04_02 Verso, autres fonctionnalités`)
