import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateToNewOffererAs } from './helpers/navigations'
import { getSirenRequestMockAs } from './helpers/sirenes'
import { createUserRole } from './helpers/roles'

const addressInput = Selector('input#offerer-address')
const nameInput = Selector('input#offerer-name')
const sirenInput = Selector('#offerer-siren')
const sirenErrorInput = Selector('#offerer-siren-error')
const submitButton = Selector('button.button.is-primary')

let user
let userRole
let dataFromSandbox
fixture('Offerer A | Créer une nouvelle structure').beforeEach(async t => {
  if (!userRole) {
    dataFromSandbox = await fetchSandbox(
      'pro_04_offerer',
      'get_existing_pro_validated_user_with_first_offerer'
    )
    user = dataFromSandbox.user
    userRole = createUserRole(user)
  }
  return navigateToNewOffererAs(user, userRole)(t)
})

test('Je peux naviguer vers une nouvelle structure et revenir aux structures', async t => {
  // given
  const backAnchor = Selector('.back-button')
  const location = await t.eval(() => window.location)

  // then
  await t.expect(location.pathname).eql('/structures/creation')

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
    .eql('/structures/creation')
    .typeText(sirenInput, '69256356275794356243264')

  // when
  await t.click(submitButton)

  // then
  await t.expect(sirenErrorInput.innerText).contains('Siren invalide')
})

test('Je ne peux pas ajouter de nouvelle structure ayant un siren déjà existant dans la base', async t => {
  // given
  const { offerer } = dataFromSandbox
  await t.addRequestHooks(getSirenRequestMockAs(offerer))
  const { siren } = offerer
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/structures/creation')
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

test('Je renseigne une nouvelle structure via son siren', async t => {
  // given
  const address = '10 PLACE JEAN JAURES'
  const name = 'NOUVEAU THEATRE DE MONTREUIL'
  const siren = '323339762'
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/structures/creation')
    .typeText(sirenInput, siren)
  await t.expect(nameInput.value).eql(name)
  await t.expect(addressInput.value).eql(address)

  // when
  await t.click(submitButton)

  // then
  location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures')
})

test("Je renseigne une structure dont l'adresse n'est pas renvoyée par l'API Siren et je peux valider", async t => {
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
  let location

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
