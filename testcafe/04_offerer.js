import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { navigateToNewOffererAs } from './helpers/navigations'
import { getSirenRequestMockAs } from './helpers/sirenes'
import { createUserRole } from './helpers/roles'

const addressInput = Selector('input[name=address]')
const nameInput = Selector('input[name=name]')
const sirenInput = Selector('input[name=siren]')
const sirenErrorInput = Selector('.field-errors')
const submitButton = Selector('button[type=submit]')

let user
let userRole
let dataFromSandbox

fixture.only("En étant sur la page de création d'une structure").beforeEach(async t => {
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

test("Je peux créer une nouvelle structure avec un nouveau SIREN n'existant pas en base de données, et je suis redirigé·e vers mes structures", async t => {
  // given
  const address = '10 PLACE JEAN JAURES'
  const name = 'NOUVEAU THEATRE DE MONTREUIL'
  const siren = '323339762'

  // when
  await t
    .typeText(sirenInput, siren)
    .expect(nameInput.value)
    .eql(name)
    .expect(addressInput.value)
    .eql(address)
    .click(submitButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures')
})

test('Je ne peux pas créer une nouvelle structure avec un SIREN invalide', async t => {
  // when
  await t.typeText(sirenInput, '69256356275794356243264').click(submitButton)

  // then
  await t.expect(sirenErrorInput.innerText).contains('Ce SIREN n\'est pas reconnu')
})

test("Je peux créer une nouvelle structure avec un SIREN dont l'adresse n'est pas renvoyée par l'API sirene, et je suis redirigé·e vers mes structures", async t => {
  // given
  const offererWithoutAddress = {
    address: null,
    city: 'Paris',
    latitude: '12.98723',
    longitude: '87.01821',
    name: 'Structure sans addresse',
    postalCode: '75000',
    siren: '216701375',
  }
  const { siren } = offererWithoutAddress
  await t.addRequestHooks(getSirenRequestMockAs(offererWithoutAddress))

  // when
  await t
    .typeText(sirenInput, siren)
    .expect(addressInput.value)
    .eql('')
    .click(submitButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures')
})
