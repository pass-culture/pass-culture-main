import { ClientFunction, Selector } from 'testcafe'

import { getPathname } from './helpers/location'
import { HOME_URL, navigateToNewOffererAs } from './helpers/navigations'
import { createUserRole } from './helpers/roles'
import { fetchSandbox } from './helpers/sandboxes'
import {
  getSirenRequestMockAs,
  getSirenRequestMockWithNoResult,
} from './helpers/sirenes'

fixture('Structure,')

test('en étant sur la page de création d’une structure', async t => {
  const dataFromSandbox = await fetchSandbox(
    'pro_04_offerer',
    'get_existing_pro_validated_user_with_first_offerer'
  )
  const user = dataFromSandbox.user
  const userRole = createUserRole(user)
  const sirenInput = Selector('input[name=siren]')
  const sirenErrorInput = Selector('.it-errors')
  const submitButton = Selector('button[type=submit]')
  const formSelector = Selector('form')
  const getFormContent = ClientFunction(() => formSelector().innerHTML, {
    dependencies: { formSelector },
  })
  await navigateToNewOffererAs(user, userRole)(t)

  // Je peux créer une nouvelle structure avec un nouveau SIREN n'existant pas en base de données, et je suis redirigé·e vers la page d'accueil
  const offererWithAddress = {
    address: '10 PLACE JEAN JAURES',
    city: 'Paris',
    latitude: '12.98723',
    longitude: '87.01821',
    name: 'NOUVEAU THEATRE DE MONTREUIL',
    postalCode: '75000',
    siren: '323339762',
  }

  await t
    .addRequestHooks(getSirenRequestMockAs(offererWithAddress))
    .typeText(sirenInput, offererWithAddress.siren, { paste: true })
    .expect(getFormContent())
    .contains('MINISTERE DE LA CULTURE')
    .expect(getFormContent())
    .contains('3 RUE DE VALOIS - 75001 Paris')
    .click(submitButton())
    .expect(getPathname())
    .eql(HOME_URL)

  // Je peux créer une nouvelle structure avec un SIREN dont l'adresse n'est pas renvoyée par l'API sirene, et je suis redirigé·e vers la page d'accueil
  await navigateToNewOffererAs(user, userRole)(t)

  const offererWithoutAddress = {
    address: null,
    city: 'Paris',
    latitude: '12.98723',
    longitude: '87.01821',
    name: 'Structure sans addresse',
    postalCode: '75000',
    siren: '216701375',
  }

  await t
    .addRequestHooks(getSirenRequestMockAs(offererWithoutAddress))
    .typeText(sirenInput, offererWithoutAddress.siren, { paste: true })
    .click(submitButton)
    .expect(getPathname())
    .eql(HOME_URL)

  // Je ne peux pas créer une nouvelle structure avec un SIREN invalide
  await navigateToNewOffererAs(user, userRole)(t)

  await t
    .addRequestHooks(getSirenRequestMockWithNoResult())
    .typeText(sirenInput, '000000000', { paste: true })
    .click(submitButton)
    .expect(sirenErrorInput.innerText)
    .contains("Ce SIREN n'est pas reconnu")
})
