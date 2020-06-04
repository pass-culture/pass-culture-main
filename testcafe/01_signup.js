import { Selector, RequestMock } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { fetchSandbox } from './helpers/sandboxes'

const emailInput = Selector('input[name="email"]')
const passwordInput = Selector('input[name="password"]')
const lastNameInput = Selector('input[name="lastName"]')
const firstNameInput = Selector('input[name="firstName"]')
const phoneNumberInput = Selector('input[name="phoneNumber"]')
const sirenInput = Selector('input[name="siren"]')
const newsletterOkInput = Selector('input[name="newsletter_ok"]')
const contactOkInput = Selector('input[name="contact_ok"]')
const cguOkInput = Selector('input[name="cgu_ok"]')
const signUpButton = Selector('button.button.is-primary')
const acceptCookieButton = Selector('#hs-eu-confirmation-button')

const mockedResponse = {
  'unite_legale': {
    'id': 11654265,
    'siren': '501106520',
    'denomination': 'WEBEDIA',
    'etablissement_siege': {
      'code_postal': '92300',
      'libelle_commune': 'LEVALLOIS-PERRET',
      'enseigne_1': null,
      'longitude': '2.276981',
      'latitude': '48.893131',
      'geo_l4': '2 RUE PAUL VAILLANT COUTURIER',
    },
  }
}

const mock = response => {
  return RequestMock()
    .onRequestTo(/\/entreprise.data.gouv.fr\/api\/sirene\/v3\/unites_legales\/.*/)
    .respond(response, 200, {
      'content-type': 'application/json; charset=utf-8',
      'access-control-allow-origin': '*'
    })
}

fixture("Création d'un compte utilisateur·trice")
  .page(`${ROOT_PATH + 'inscription'}`)

test.requestHooks(mock(mockedResponse))("Je peux créer un compte avec un SIREN non existant en base de données," +
  " et je suis redirigé·e vers la page de confirmation de l'inscription", async t => {
  // given
  const email = 'pctest0.pro93.cafe0@btmx.fr'
  const firstName = 'PC Test 0 Pro'
  const lastName = '93 Café0'
  const phoneNumber = '0102030405'
  const password = 'user@AZERTY123'
  const siren = '501106520'

  // when
  await t
    .click(acceptCookieButton)
    .typeText(emailInput, email)
    .typeText(passwordInput, password)
    .typeText(lastNameInput, lastName)
    .typeText(firstNameInput, firstName)
    .typeText(phoneNumberInput, phoneNumber)
    .typeText(sirenInput, siren)

  // then
  await t.expect(signUpButton.hasAttribute('disabled')).ok()

  // when
  await t
    .click(newsletterOkInput)
    .click(contactOkInput)
    .click(cguOkInput)
    .click(signUpButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription/confirmation')
})

test.requestHooks(mock(mockedResponse))("Je peux créer un compte avec un SIREN déjà existant en base de données," +
  " et je suis redirigé·e vers la page de confirmation de l'inscription", async t => {
  // given
  const { offerer } = await fetchSandbox('pro_01_signup', 'get_existing_pro_user_with_offerer')
  const email = 'pctest0.pro93.cafe1@btmx.fr'
  const firstName = 'PC Test Pro'
  const lastName = '93 Café1'
  const phoneNumber = '0102030405'
  const password = 'user@AZERTY123'
  const { siren } = offerer

  // when
  await t
    .click(acceptCookieButton)
    .typeText(emailInput, email)
    .typeText(passwordInput, password)
    .typeText(lastNameInput, lastName)
    .typeText(firstNameInput, firstName)
    .typeText(phoneNumberInput, phoneNumber)
    .typeText(sirenInput, siren)
    .click(contactOkInput)
    .click(newsletterOkInput)
    .click(cguOkInput)
    .click(signUpButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription/confirmation')
})

test('Lorsque je clique sur le lien de validation de création du compte reçu par email, je suis redirigé·e vers la page de connexion', async t => {
  // given
  const { user } = await fetchSandbox(
    'pro_01_signup',
    'get_existing_pro_not_validated_user_with_real_offerer'
  )
  const { validationToken } = user

  // when
  await t.navigateTo('/inscription/validation/' + validationToken)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test('La balise script pour le tracking HubSpot est présente sur la page', async t => {
  // given - when
  const trackingScript = Selector('script[src="//js.hs-scripts.com/5119289.js"]')

  // then
  await t.expect(trackingScript.exists).ok()
})
