import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { offererUser0, offererUser1 } from './helpers/users'

const contactOkInput = Selector('#user-contact_ok')
const contactOkInputError = Selector('#user-contact_ok-error')
const emailInput = Selector('#user-email')
const emailInputError = Selector('#user-email-error')
const firstNameInput = Selector('#user-firstName')
const lastNameInput = Selector('#user-lastName')
const newsletterOkInput = Selector('#user-newsletter_ok')
const passwordInput = Selector('#user-password')
const passwordInputError = Selector('#user-password-error')
const publicNameInput = Selector('#user-publicName')
const signInButton = Selector('.is-secondary').withText("J'ai déjà un compte")
const signUpButton = Selector('button.button.is-primary')
const sirenInput = Selector('#user-siren')
const sirenInputError = Selector('#user-siren-error')
const pendingOffererList = Selector('#pending-offerer-list')
const firstPendingOffererName = Selector(
  '#pending-offerer-list .list-content p span'
)
const notificationSuccess = Selector('.notification.is-success')

fixture`01_01 SignupPage |  Component | Je crée un compte utilisateur·ice`
  .page`${ROOT_PATH + 'inscription'}`

test("Je peux cliquer sur lien pour me connecter si j'ai déja un compte", async t => {
  await t.click(signInButton)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test("Lorsque l'un des champs obligatoire est manquant, le bouton créer est desactivé", async t => {
  await t.typeText(emailInput, 'email@email.test')
  await t.expect(signUpButton.innerText).eql('Créer')
  await t.expect(signUpButton.hasAttribute('disabled')).ok()
})

test('Je créé un compte, je suis redirigé·e vers la page /inscription/confirmation', async t => {
  await t
    .typeText(publicNameInput, offererUser0.publicName)
    .typeText(emailInput, offererUser0.email)
    .typeText(passwordInput, offererUser0.password)
    .typeText(lastNameInput, offererUser0.lastName)
    .typeText(firstNameInput, offererUser0.firstName)
    .typeText(sirenInput, offererUser0.siren)

    .expect(signUpButton.hasAttribute('disabled'))
    .ok()
    .click(contactOkInput)
    .click(newsletterOkInput)

  await t.click(signUpButton)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription/confirmation')
})

fixture`01_02 SignupPage | Création d'un compte utilisateur | Messages d'erreur lorsque les champs ne sont pas correctement remplis`
  .page`${ROOT_PATH + 'inscription'}`

test.skip('E-mail déjà présent dans la base et mot de passe invalide', async t => {
  await t
    .typeText(publicNameInput, offererUser0.publicName)
    .typeText(emailInput, offererUser0.email)
    .typeText(passwordInput, 'pas')
    .typeText(sirenInput, offererUser0.siren)

    .click(contactOkInput)

  await t.click(signUpButton)

  await t
    .expect(emailInputError.innerText)
    .eql('\nUn compte lié à cet email existe déjà\n\n')
  // TODO Mot de passe invalide en attente correction API
  // await t.expect(passwordInputError.innerText).eql(" Vous devez saisir au moins 8 caractères.\n")
})

fixture`01_03 SignupPage | Création d'un compte pour rattachement à une structure existante`
  .page`${ROOT_PATH + 'inscription'}`

test('Je créé un compte, je suis redirigé·e vers la page /inscription/confirmation', async t => {
  await t
    .typeText(publicNameInput, offererUser1.publicName)
    .typeText(emailInput, offererUser1.email)
    .typeText(passwordInput, offererUser1.password)
    .typeText(lastNameInput, offererUser1.lastName)
    .typeText(firstNameInput, offererUser1.firstName)
    .typeText(sirenInput, offererUser1.siren)

    .expect(signUpButton.hasAttribute('disabled'))
    .ok()
    .click(contactOkInput)
    .click(newsletterOkInput)

  await t.click(signUpButton)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription/confirmation')
})

test('Je demande le rattachement à une structure existante', async t => {})

fixture`01_04 SignupPage | Clique sur le lien de validation de compte reçu par email`
  .page`${ROOT_PATH + 'inscription'}`

test('Je suis redirigé sur la page de connexion avec un message de confirmation', async t => {
  // when
  await t.navigateTo('/inscription/validation/AZERTY123').wait(500)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
  await t.expect(notificationSuccess.exists).ok()
})
