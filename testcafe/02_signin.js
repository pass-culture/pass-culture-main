import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER } from './helpers/users'

const inputUsersIdentifier = Selector('#user-identifier')
const inputUsersIdentifierError = Selector('#user-identifier-error')
const inputUsersPassword = Selector('#user-password')
const inputUsersPasswordError = Selector('#user-password-error')
const pageTitle = Selector('h1')
const signInButton = Selector('button.button.is-primary') //connexion
const signUpButton = Selector('.is-secondary') // inscription

fixture`SignInPage A | J'ai un compte et je me connecte`.page`${ROOT_PATH +
  'connexion'}`

test('Je peux cliquer sur lien Créer un compte', async t => {
  // when
  await t.click(signUpButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription')
})

test("Lorsque l'un des deux champs est manquant, le bouton connexion est desactivé", async t => {
  // given
  const { email } = EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER

  // when
  await t.typeText(inputUsersIdentifier, email)

  // then
  await t.expect(signInButton.hasAttribute('disabled')).ok()
})

test("J'ai un compte valide, en cliquant sur 'se connecter' je suis redirigé·e vers la page /offres sans erreurs", async t => {
  // given
  const { email, password } = EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER

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
  const { email, password } = EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER

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

test("J'ai un compte Identifiant invalide, je vois un messages d'erreur et je reste sur la page /connection", async t => {
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

test("J'ai un mot de passe invalide, je vois un messages d'erreur et je reste sur la page /connection", async t => {
  // given
  const { email } = EXISTING_VALIDATED_UNREGISTERED_93_OFFERER_USER

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

fixture`SignInPage B | J'accède à une page sans être connecté·e`
  .page`${ROOT_PATH + 'offres'}`

test('Je suis redirigé·e vers la page connexion', async t => {
  await t
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})
