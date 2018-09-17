import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import youngUser from './helpers/users'



const userIdentifier = Selector('#user-identifier')
const userPassword = Selector('#user-password')
const userIdentifierError = Selector('#user-identifier-error')
const userPasswordError = Selector('#user-password-error')
const signInButton = Selector('button').withText('Connexion')
const signUpButton = Selector('.is-secondary')

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

    .typeText(userIdentifier, youngUser.email)
    .wait(1000)
    .expect(signInButton.hasAttribute('disabled'))
    .ok()
})

test("J'ai un compte valide, je suis redirigé·e vers la page /decouverte sans erreurs", async t => {
  await t
    .typeText(userIdentifier, youngUser.email)
    .typeText(userPassword, youngUser.password)
    .wait(1000)
    .click(signInButton)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/decouverte')
})

test("J'ai un identifiant invalide, je vois un messages d'erreur et je reste sur la page /connection", async t => {
  await t
    .typeText(userIdentifier, 'wrongEmail@test.com')
    .typeText(userPassword, 'Pa$$word')
    .wait(1000)
    .click(signInButton)
    .wait(1000)
  await t
    .expect(userIdentifierError.innerText)
    .eql('\nIdentifiant incorrect\n\n')

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test("J'ai un mot de passe invalide, je vois un message d'erreur et je reste sur la page /connection", async t => {
  await t
    .typeText(userIdentifier, youngUser.email)
    .typeText(userPassword, 'Pa$$word')
    .wait(1000)
    .click(signInButton)
    .wait(1000)

  await t
    .expect(userPasswordError.innerText)
    .eql('\nMot de passe incorrect\n\n')

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

// TODO
// 1 Quand on clique sur l'icone 'eye' on peut lire le mot de userPasswordError
// 2 Texte de présentation (Identifiez-vous, etc.)
