import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import {
  navigateToNewOffererAs,
  navigateToOffererAs,
} from './helpers/navigations'
import { getSirenRequestMockAs } from './helpers/sirenes'

const addressInput = Selector('input#offerer-address')
const nameInput = Selector('input#offerer-name')
const sirenInput = Selector('#offerer-siren')
const sirenErrorInput = Selector('#offerer-siren-error')
const submitButton = Selector('button.button.is-primary')

fixture('Offerer A | Créer une nouvelle structure').beforeEach(async t => {
  t.ctx.sandbox = await fetchSandbox(
    'pro_04_offerer',
    'get_existing_pro_validated_user_with_first_offerer'
  )
  const { user } = t.ctx.sandbox
  return navigateToNewOffererAs(user)(t)
})

test('Je peux naviguer vers une nouvelle structure et revenir aux structures', async t => {
  // given
  const backAnchor = Selector('a.button.is-secondary')
  const location = await t.eval(() => window.location)

  // then
  await t.expect(location.pathname).eql('/structures/nouveau')

  // when
  await t.click(backAnchor)

  // then
  const newLocation = await t.eval(() => window.location)
  await t.expect(newLocation.pathname).eql('/structures')
})

test('Je ne peux pas ajouter de nouvelle structure avec un siren faux', async t => {
  // given
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/structures/nouveau')
    .typeText(sirenInput, '69256356275794356243264')

  // when
  await t.click(submitButton)

  // then
  await t.expect(sirenErrorInput.innerText).contains('Siren invalide')
})

test('Je ne peux pas ajouter de nouvelle structure ayant un siren déjà existant dans la base', async t => {
  // given
  const { offerer } = t.ctx.sandbox
  await t.addRequestHooks(getSirenRequestMockAs(offerer))
  const { siren } = offerer
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/structures/nouveau')
    .typeText(sirenInput, siren)

  // when
  await t.click(submitButton)

  // when
  await t
    .expect(sirenErrorInput.innerText)
    .contains(
      'Une entrée avec cet identifiant existe déjà dans notre base de données'
    )
})

test('Je rentre une nouvelle structure via son siren', async t => {
  // given
  const address = '10 PLACE JEAN JAURES'
  const name = 'NOUVEAU THEATRE DE MONTREUIL'
  const siren = '323339762'
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/structures/nouveau')
    .typeText(sirenInput, siren)
  await t.expect(nameInput.value).eql(name)
  await t.expect(addressInput.value).eql(address)

  // when
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures')
})

test("Je rentre une structure dont l'adresse n'est pas renvoyée par l'api sirene et je peux valider", async t => {
  // given
  const futureOffererWithNoAddress = {
    address: null,
    city: 'Samoix Jsaispas',
    latitude: '12.98723',
    longitude: '87.01821',
    name: 'Structure sans addresse',
    postalCode: '75000',
    siren: '216701375',
  }
  const { siren } = futureOffererWithNoAddress
  await t.addRequestHooks(getSirenRequestMockAs(futureOffererWithNoAddress))
  let location = await t.eval(() => window.location)

  // when
  await t
    .typeText(sirenInput, siren)
    .expect(addressInput.value)
    .eql('')
    .click(submitButton)

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures')
})

fixture('Offerer B | Modifier une structure')

test.skip('Je modifie une structure pour lui ajouter ses coordonnées bancaires car je suis admin', async t => {
  // given
  const { offerer, user } = await fetchSandbox(
    'pro_04_offerer',
    'get_existing_pro_validated_user_with_offerer_with_no_iban'
  )
  await navigateToOffererAs(user, offerer)(t)

  // when
  // t.typeText(bicInput, 'BNPAFRPP')
  // t.typeText(ibanInput, 'FR7630004000031234567890143')

  // then
  // TODO
})
