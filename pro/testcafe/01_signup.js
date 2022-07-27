import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'

import { getPathname } from './helpers/location'
import { fetchSandbox } from './helpers/sandboxes'
import { getSirenRequestMockWithDefaultValues } from './helpers/sirenes'

const emailInput = Selector('input[name="email"]')
const passwordInput = Selector('input[name="password"]')
const lastNameInput = Selector('input[name="lastName"]')
const firstNameInput = Selector('input[name="firstName"]')
const phoneNumberInput = Selector('input[name="phoneNumber"]')
const sirenInput = Selector('input[name="siren"]')
const contactOkInput = Selector('input[name="contactOk"]')
const signUpButton = Selector('button').withText('Créer mon compte')
const acceptCookieButton = Selector('#hs-eu-confirmation-button')

fixture('Création d’un compte utilisateur·trice,').page(
  `${ROOT_PATH}inscription`
)

test('je peux créer un compte avec un SIREN non existant en base de données, et je suis redirigé·e vers la page de confirmation de l’inscription', async t => {
  await acceptCookieButton()

  await t
    .addRequestHooks(getSirenRequestMockWithDefaultValues())
    .click(acceptCookieButton)
    .expect(signUpButton.hasAttribute('disabled'))
    .ok()
    .typeText(emailInput, 'pctest0.pro93.cafe0@example.com', { paste: true })
    .typeText(passwordInput, 'user@AZERTY123', { paste: true })
    .typeText(lastNameInput, '93 Café0', { paste: true })
    .typeText(firstNameInput, 'PC Test 0 Pro', { paste: true })
    .typeText(phoneNumberInput, '0102030405', { paste: true })
    .typeText(sirenInput, '501106520')
    .pressKey('tab')
    .click(signUpButton)
    .expect(getPathname())
    .eql('/inscription/confirmation')
})

test('je peux créer un compte avec un SIREN déjà existant en base de données, et je suis redirigé·e vers la page de confirmation de l’inscription', async t => {
  const { offerer } = await fetchSandbox(
    'pro_01_signup',
    'get_existing_pro_user_with_offerer'
  )
  await acceptCookieButton()

  await t
    .addRequestHooks(getSirenRequestMockWithDefaultValues())
    .click(acceptCookieButton)
    .typeText(emailInput, 'pctest0.pro93.cafe1@example.com', { paste: true })
    .typeText(passwordInput, 'user@AZERTY123', { paste: true })
    .typeText(lastNameInput, '93 Café1', { paste: true })
    .typeText(firstNameInput, 'PC Test Pro', { paste: true })
    .typeText(phoneNumberInput, '0102030405', { paste: true })
    .typeText(sirenInput, offerer.siren, { paste: true })
    .click(contactOkInput)
    .click(signUpButton)
    .expect(getPathname())
    .eql('/inscription/confirmation')
})

test('lorsque je clique sur le lien de validation de création du compte reçu par email, je suis redirigé·e vers la page de connexion', async t => {
  const { user } = await fetchSandbox(
    'pro_01_signup',
    'get_existing_pro_not_validated_user_with_real_offerer'
  )

  await t
    .navigateTo(`/inscription/validation/${user.validationToken}`)
    .expect(getPathname())
    .eql('/connexion')
})

test('la balise script pour le tracking HubSpot est présente sur la page', async t => {
  const trackingScript = Selector('script').withAttribute(
    'src',
    /.*\/\/js\.hs-scripts.com\/5119289\.js/
  )
  await t.expect(trackingScript.exists).ok()
})
