import { ClientFunction, Selector } from 'testcafe'
import { youngUser } from './helpers/users'

import { ROOT_PATH } from '../src/utils/config'

const getPageUrl = ClientFunction(() => window.location.href.toString())

const userId = '#user-identifier'
const passId = '#user-password'
const errorClass = '.pc-error-message'
const userPassword = Selector(passId)
const userIdentifier = Selector(userId)
const passwordError = Selector(`${passId}-error`).find(errorClass)
const identifierErrors = Selector(`${userId}-error`).find(errorClass)
const signInButton = Selector('#signin-submit-button')
// const signUpButton = Selector('#signin-signup-button')

fixture("02_01 SignInPage Component | J'ai un compte et je me connecte").page(
  `${ROOT_PATH}connexion`
)

// test('Je peux cliquer sur lien /inscription', async t => {
//   await t.click(signUpButton)
//   const location = await t.eval(() => window.location)
//   await t.expect(location.pathname).eql('/inscription')
// })

test("Lorsque l'un des deux champs est manquant, le bouton connexion est désactivé", async t => {
  await t
    .typeText(userIdentifier, youngUser.email)
    .expect(signInButton.hasAttribute('disabled'))
    .ok()
})

test("J'ai un compte valide, je suis redirigé·e vers la page /decouverte sans erreurs", async t => {
  await t
    .typeText(userIdentifier, youngUser.email)
    .typeText(userPassword, youngUser.password)
    .click(signInButton)
    .wait(1000)

  const location = await t.eval(() => window.location)
  await t
    .expect(identifierErrors.count)
    .eql(0)
    .expect(location.pathname)
  await t.expect(getPageUrl()).contains('/decouverte', { timeout: 1000 })
})

test("J'ai un identifiant invalide, je vois un messages d'erreur et je reste sur la page /connection", async t => {
  await t
    .typeText(userIdentifier, 'wrongEmail@test.com')
    .typeText(userPassword, youngUser.password)
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

test("J'ai un mot de passe vide, avant envoi à l'API, je vois un message d'erreur et je reste sur la page /connection", async t => {
  await t
    // saisi du mot de passe
    .typeText(userPassword, youngUser.password)
    // puis on l'efface
    // - prevent testcafe de warn sur une valeur vide
    // TODO -> trouver une solution pour Blue le password input
    // faire plus propre
    .selectText(userPassword)
    .pressKey('delete')
    .typeText(userIdentifier, youngUser.email)
    // .click(signInButton)
    .wait(1000)

  const location = await t.eval(() => window.location)
  await t
    .expect(passwordError.count)
    .gte(1)
    .expect(passwordError.nth(0).innerText)
    .eql('Ce champs est requis.')
    .expect(location.pathname)
    .eql('/connexion')
})

test("J'ai un mot de passe invalide, je vois un message d'erreur et je reste sur la page /connection", async t => {
  await t
    .typeText(userIdentifier, youngUser.email)
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
