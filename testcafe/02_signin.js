import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const inputUsersIdentifier = Selector('#user-identifier')
const inputUsersIdentifierError = Selector('#user-identifier-error')
const inputUsersPassword = Selector('#user-password')
const inputUsersPasswordError = Selector('#user-password-error')
const pageTitle = Selector('h1')
const signInButton = Selector('button.button.is-primary')
const signUpButton = Selector('.is-secondary')

fixture('SignInPage A | Je me connecte avec un compte validé')
  .page(`${ROOT_PATH + 'connexion'}`)
  .beforeEach(async t => {
    t.ctx.sandbox = await fetchSandbox(
      'pro_02_signin',
      'get_existing_pro_validated_user'
    )
  })

test('Je peux cliquer sur lien Créer un compte', async t => {
  // when
  await t.click(signUpButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription')
})

test("Lorsque l'un des deux champs est manquant, le bouton connexion est désactivé", async t => {
  // given
  const { user } = t.ctx.sandbox
  const { email } = user

  // when
  await t.typeText(inputUsersIdentifier, email)

  // then
  await t.expect(signInButton.hasAttribute('disabled')).ok()
})

test("J'ai un compte valide, en cliquant sur 'se connecter' je suis redirigé·e vers la page /offres sans erreurs", async t => {
  // given
  const { user } = t.ctx.sandbox
  const { email, password } = user

  // when
  await t
    .typeText(inputUsersIdentifier, email)
    .typeText(inputUsersPassword, password)
    .click(signInButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
  await t.expect(pageTitle.innerText).eql('Vos offres')
})

test("J'ai un compte valide, en appuyant sur la touche 'Entrée' je suis redirigé·e vers la page /offres sans erreurs", async t => {
  // given
  const { user } = t.ctx.sandbox
  const { email, password } = user

  // when
  await t
    .typeText(inputUsersIdentifier, email)
    .typeText(inputUsersPassword, password)
    .pressKey('Enter')

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
  await t.expect(pageTitle.innerText).eql('Vos offres')
})

test("J'ai un email incorrect, je vois un messages d'erreur et je reste sur la page /connection", async t => {
  // when
  await t
    .typeText(inputUsersIdentifier, 'email@email.test')
    .typeText(inputUsersPassword, 'Pa$$word')
    .click(signInButton)

  // then
  await t
    .expect(inputUsersIdentifierError.innerText)
    .contains('Identifiant incorrect')
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test("J'ai un mot de passe incorrect, je vois un messages d'erreur et je reste sur la page /connection", async t => {
  // given
  const { user } = t.ctx.sandbox
  const { email } = user

  // when
  await t
    .typeText(inputUsersIdentifier, email)
    .typeText(inputUsersPassword, 'Pa$$word')
    .click(signInButton)

  // then
  await t
    .expect(inputUsersPasswordError.innerText)
    .contains('Mot de passe incorrect')
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

fixture('SignInPage B | Je me connecte avec un compte pas encore validé')
  .page(`${ROOT_PATH + 'connexion'}`)
  .beforeEach(async t => {
    t.ctx.sandbox = await fetchSandbox(
      'pro_02_signin',
      'get_existing_pro_not_validated_user'
    )
  })

test("Je vois un messages d'erreur et je reste sur la page /connection", async t => {
  // given
  const { user } = t.ctx.sandbox
  const { email, password } = user

  // when
  await t
    .typeText(inputUsersIdentifier, email)
    .typeText(inputUsersPassword, password)
    .click(signInButton)

  // then
  await t
    .expect(inputUsersIdentifierError.innerText)
    .contains("Ce compte n'est pas validé")
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

fixture("SignInPage C | J'accède à une page sans être connecté·e").page(
  `${ROOT_PATH + 'offres'}`
)

test('Je suis redirigé·e vers la page connexion', async t => {
  await t
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})
