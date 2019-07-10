import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { fetchSandbox } from './helpers/sandboxes'
import { getSirenRequestMockAs } from './helpers/sirenes'

const cguOkInput = Selector('#user-cgu_ok')
const contactOkInput = Selector('#user-contact_ok')
const emailInput = Selector('#user-email')
const emailInputError = Selector('#user-email-error')
const firstNameInput = Selector('#user-firstName')
const lastNameInput = Selector('#user-lastName')
const newsletterOkInput = Selector('#user-newsletter_ok')
const notificationSuccess = Selector('.notification.is-success')
const passwordInput = Selector('#user-password')
const passwordInputError = Selector('#user-password-error')
const signInButton = Selector('.is-secondary').withText("J'ai déjà un compte")
const signUpButton = Selector('button.button.is-primary')
const sirenInput = Selector('#user-siren')

fixture('Signup A | Je crée un compte utilisateur·ice').page(
  `${ROOT_PATH + 'inscription'}`
)

test("Je peux cliquer sur le lien pour me connecter si j'ai déjà un compte", async t => {
  // when
  await t.click(signInButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test("Lorsque l'un des champs obligatoires est manquant, le bouton créer est désactivé", async t => {
  // given
  await t.typeText(emailInput, 'email@email.test')

  // when
  await t.click(cguOkInput)

  // then
  await t.expect(signUpButton.innerText).eql('Créer')
  await t.expect(signUpButton.hasAttribute('disabled')).ok()
})

test('Je créé un compte avec un nouveau siren, je suis redirigé·e vers la page /inscription/confirmation', async t => {
  // given
  const email = 'pctest0.pro93.cafe0@btmx.fr'
  const firstName = 'PC Test 0 Pro'
  const lastName = '93 Café0'
  const password = 'user@AZERTY123'
  const siren = '501106520'

  // then
  await t
    .typeText(emailInput, email)
    .typeText(passwordInput, password)
    .typeText(lastNameInput, lastName)
    .typeText(firstNameInput, firstName)
    .typeText(sirenInput, siren)

  // then
  await t.expect(signUpButton.hasAttribute('disabled')).ok()

  // when
  await t
    .click(contactOkInput)
    .click(cguOkInput)
    .click(newsletterOkInput)
    .click(signUpButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription/confirmation')
})

let dataFromSandbox
fixture(
  "Signup B | Création d'un compte utilisateur et messages d'erreur lorsque les champs ne sont pas correctement remplis"
)
  .page(`${ROOT_PATH + 'inscription'}`)
  .beforeEach(async t => {
    if (!dataFromSandbox) {
      dataFromSandbox = await fetchSandbox(
        'pro_01_signup',
        'get_existing_pro_user_with_offerer'
      )
    }
    await t.addRequestHooks(getSirenRequestMockAs(dataFromSandbox.offerer))
  })

test('E-mail déjà présent dans la base', async t => {
  // given
  const { offerer, user } = dataFromSandbox
  const { email, firstName, lastName, password } = user
  const { siren } = offerer
  await t
    .typeText(emailInput, email)
    .typeText(passwordInput, password)
    .typeText(lastNameInput, lastName)
    .typeText(firstNameInput, firstName)
    .typeText(sirenInput, siren)
    .click(contactOkInput)
    .click(cguOkInput)

  // when
  await t.click(signUpButton)

  // then
  await t.expect(emailInputError.innerText).match(/.*\S.*/)
})

test('Mot de passe invalide', async t => {
  // given
  const { offerer, user } = dataFromSandbox
  const { email, firstName, lastName } = user
  const { siren } = offerer
  await t
    .typeText(emailInput, email)
    .typeText(passwordInput, 'pas')
    .typeText(lastNameInput, lastName)
    .typeText(firstNameInput, firstName)
    .typeText(sirenInput, siren)
    .click(contactOkInput)
    .click(cguOkInput)

  // when
  await t.click(signUpButton)

  // then
  await t.expect(passwordInputError.innerText).match(/.*\S.*/)
})

fixture(
  "Signup C | Création d'un compte pour rattachement à une structure existante"
).page(`${ROOT_PATH + 'inscription'}`)

test('Je crée un compte avec un siren déjà dans la base, je suis redirigé·e vers la page /inscription/confirmation', async t => {
  // given
  const { offerer } = dataFromSandbox
  const email = 'pctest0.pro93.cafe1@btmx.fr'
  const firstName = 'PC Test Pro'
  const lastName = '93 Café1'
  const password = 'user@AZERTY123'
  const { siren } = offerer
  await t
    .typeText(emailInput, email)
    .typeText(passwordInput, password)
    .typeText(lastNameInput, lastName)
    .typeText(firstNameInput, firstName)
    .typeText(sirenInput, siren)
    .click(contactOkInput)
    .click(newsletterOkInput)
    .click(cguOkInput)

  // when
  await t.click(signUpButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription/confirmation')
})

fixture(
  'Signup D | Clic sur le lien de validation de compte reçu par email'
).page(`${ROOT_PATH + 'inscription'}`)

test('Je suis redirigé·e vers la page de connexion avec un message de confirmation', async t => {
  // given
  const { user } = await fetchSandbox(
    'pro_01_signup',
    'get_existing_pro_not_validated_user_with_real_offerer'
  )
  const { validationToken } = user

  // when
  await t
    .navigateTo(`/inscription/validation/${validationToken}`)
    // please be careful, this wait prevents is necessary
    // to pass every time, otherwise success of this test is
    // kind of random!
    .wait(10000)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
  await t.expect(notificationSuccess.exists).ok()
})
