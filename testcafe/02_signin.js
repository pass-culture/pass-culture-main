import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import userFromSandboxDB from './helpers/users'

const userId = '#user-identifier'
const passId = '#user-password'
const errorClass = '.pc-error-message'
const userPassword = Selector(passId)
const userIdentifier = Selector(userId)
const passwordError = Selector(`${passId}-error`).find(errorClass)
const identifierErrors = Selector(`${userId}-error`).find(errorClass)
const signInButton = Selector('#signin-submit-button')
const signUpButton = Selector('#signin-signup-button')

fixture("02_01 SignInPage Component | J'ai un compte et je me connecte").page(
  `${ROOT_PATH}connexion`
)

test('Je peux cliquer sur lien /inscription', async t => {
  await t.click(signUpButton)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription')
})

test("Lorsque l'un des deux champs est manquant, le bouton connexion est désactivé", async t => {
  await t
    .typeText(userIdentifier, userFromSandboxDB.email)
    .expect(signInButton.hasAttribute('disabled'))
    .ok()
})

test("J'ai un compte valide, je suis redirigé·e vers la page /decouverte sans erreurs", async t => {
  await t
    .typeText(userIdentifier, userFromSandboxDB.email)
    .typeText(userPassword, userFromSandboxDB.password)
    .click(signInButton)
    .wait(1000)

  const location = await t.eval(() => window.location)
  await t
    .expect(identifierErrors.count)
    .eql(0)
    .expect(location.pathname)
    .eql('/decouverte')
})

test("J'ai un identifiant invalide, je vois un messages d'erreur et je reste sur la page /connection", async t => {
  await t
    .typeText(userIdentifier, 'wrongEmail@test.com')
    .typeText(userPassword, userFromSandboxDB.password)
    .click(signInButton)
    .wait(1000)

  const location = await t.eval(() => window.location)
  await t
    .expect(identifierErrors.count)
    .gte(1)
    .expect(identifierErrors.nth(0).innerText)
    .eql('Identifiant incorrect')
    .expect(location.pathname)
    .eql('/connexion')
})

test("J'ai un mot de passe invalide, envoi avant à l'API, je vois un message d'erreur et je reste sur la page /connection", async t => {
  await t
    .typeText(userIdentifier, userFromSandboxDB.email)
    .typeText(userPassword, 'Pa$$word42')
    .click(signInButton)
    .wait(1000)

  const location = await t.eval(() => window.location)
  await t
    .expect(passwordError.count)
    .gte(1)
    .expect(passwordError.nth(0).innerText)
    .eql(
      'Le mot de passe doit contenir au minimum 12 caractères, un chiffre, une majuscule, une minuscule et un caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;'
    )
    .expect(location.pathname)
    .eql('/connexion')
})

test("J'ai un mot de passe invalide, je vois un message d'erreur et je reste sur la page /connection", async t => {
  await t
    .typeText(userIdentifier, userFromSandboxDB.email)
    .typeText(userPassword, 'Pa$$word4242')
    .click(signInButton)
    .wait(1000)

  const location = await t.eval(() => window.location)
  await t
    .expect(passwordError.count)
    .gte(1)
    .expect(passwordError.nth(0).innerText)
    .eql('Mot de passe incorrect')
    .expect(location.pathname)
    .eql('/connexion')
})

// TODO
// 1 Quand on clique sur l'icone 'eye' on peut lire le mot de userPasswordError
// 2 Texte de présentation (Identifiez-vous, etc.)
