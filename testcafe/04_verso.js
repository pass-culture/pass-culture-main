// ./node_modules/.bin/testcafe chrome:headless ./testcafe/04_verso.js
import { Selector } from 'testcafe'

import { getVersoWallet, getVersoWalletValue } from './helpers/getVersoWallet'
import { ROOT_PATH } from '../src/utils/config'
import { createUserRole } from './helpers/roles'
import { hasBookedSomeUser93, hasSignedUpUser93 } from './helpers/users'

const thingBaseURL = 'KU/F4'
const discoverURL = `${ROOT_PATH}decouverte`
const offerPage = `${discoverURL}/${thingBaseURL}`

const openMenu = Selector('#deck-footer .profile-button')
const openVerso = Selector('#deck-open-verso-button')

fixture(`04_01 Verso, montant du porte-monnaie`)

test(`La somme affichée est égale à 0`, async t => {
  await t.click(openMenu).wait(500)
  const versoWallet = await getVersoWallet()
  await t
    .expect(versoWallet)
    .contains('€')
    .expect(versoWallet)
    .eql('0€')
}).before(async t => {
  await t
    .useRole(createUserRole(hasSignedUpUser93))
    .navigateTo(offerPage)
    .wait(500)
})

test(`La somme affichée est supérieure à 0`, async t => {
  await t.click(openVerso).wait(500)
  const versoWallet = await getVersoWallet()
  await t.expect(versoWallet).contains('€')
  const versoWalletValue = await getVersoWalletValue()
  await t.expect(versoWalletValue).gte(0)
}).before(async t => {
  await t
    .useRole(createUserRole(hasBookedSomeUser93))
    .navigateTo(offerPage)
    .wait(500)
})

// fixture(`04_02 Verso, autres fonctionnalités`)
