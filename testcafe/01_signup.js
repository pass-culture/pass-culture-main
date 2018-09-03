import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { offererUser } from './helpers/users'

const contactOkInput = Selector('#user-contact_ok')
const contactOkInputError = Selector('#user-contact_ok-error')
const emailInput = Selector('#user-email')
const emailInputError = Selector('#user-email-error')
const passwordInput = Selector('#user-password')
const passwordInputError = Selector('#user-password-error')
const newsletterOkInput = Selector('#user-newsletter_ok')
const publicNameInput = Selector('#user-publicName')
const signInButton = Selector('.is-secondary').withText("J'ai déjà un compte")
const signUpButton = Selector('button.button.is-primary')
const sirenInput = Selector('#user-siren')
const sirenInputError = Selector('#user-siren-error')

fixture`01_01 SignupPage |  Component | Je crée un compte utilisateur·ice`
  .page`${ROOT_PATH + 'inscription'}`

test("Je peux cliquer sur lien pour me connecter si j'ai déja un compte", async t => {
  await t.click(signInButton).wait(500)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test("Lorsque l'un des champs obligatoire est manquant, le bouton créer est desactivé", async t => {
  await t.typeText(emailInput, 'email@email.test').wait(500)
  await t.expect(signUpButton.innerText).eql('Créer')
  await t.expect(signUpButton.hasAttribute('disabled')).ok()
})

test('Je créé un compte, je suis redirigé·e vers la page /structures', async t => {
  await t
    .typeText(publicNameInput, offererUser.publicName)
    .typeText(emailInput, offererUser.email)
    .typeText(passwordInput, offererUser.password)
    .typeText(sirenInput, offererUser.siren)
    .wait(3000)
    .expect(signUpButton.hasAttribute('disabled'))
    .ok()
    .click(contactOkInput)
    .click(newsletterOkInput)
    .wait(1000)

  await t.click(signUpButton).wait(5000)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures')
})

fixture`01_02 SignupPage | Création d'un compte utilisateur | Messages d'erreur lorsque les champs ne sont pas correctement remplis`
  .page`${ROOT_PATH + 'inscription'}`

test.skip('E-mail déjà présent dans la base et mot de passe invalide', async t => {
  await t
    .typeText(publicNameInput, offererUser.publicName)
    .typeText(emailInput, offererUser.email)
    .typeText(passwordInput, 'pas')
    .typeText(sirenInput, offererUser.siren)
    .wait(3000)
    .click(contactOkInput)
    .wait(1000)

  await t.click(signUpButton).wait(5000)

  await t
    .expect(emailInputError.innerText)
    .eql('\nUn compte lié à cet email existe déjà\n\n')
  // TODO Mot de passe invalide en attente correction API
  // await t.expect(passwordInputError.innerText).eql(" Vous devez saisir au moins 8 caractères.\n")
})
