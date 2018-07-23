import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { offererUser } from './helpers/users'

const errorMessages  = Selector('.errors') // inscription
const inputUsersIdentifier = Selector('#sign-in-identifier')
const inputUsersIdentifierError = Selector('#sign-in-identifier')
const inputUsersPassword = Selector('#sign-in-password')
const inputUsersPasswordError = Selector('#sign-in-password')
const signInButton  = Selector('button.button.is-primary') //connexion
const signUpButton  = Selector('.is-secondary') // inscription


fixture `02_01 SignInPage Component | J'ai un compte et je me connecte`
    .page `${ROOT_PATH+'connexion'}`

test("Je peux cliquer sur lien Créer un compte", async t => {
  await t
  .click(signUpButton)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription')
})

test("Lorsque l'un des deux champs est manquant, le bouton connexion est desactivé", async t => {
  await t
    .typeText(inputUsersIdentifier, offererUser.email)
    .wait(1000)
  await t.expect(signInButton.hasAttribute('disabled')).ok()
})

test("J'ai un compte valide, je suis redirigé·e vers la page /offres sans erreurs", async t => {

  await t
  .typeText(inputUsersIdentifier, offererUser.email)
  .typeText(inputUsersPassword, offererUser.password)
  .wait(1000)
  .click(signInButton)
  .wait(1000)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
})

test("J'ai un compte Identifiant invalide, je vois un messages d'erreur et je reste sur la page /connection", async t => {

  await t
  .typeText(inputUsersIdentifier, 'email@email.test')
  .typeText(inputUsersPassword, 'Pa$$word')
  .wait(1000)
  .click(signInButton)
  .wait(1000)

  .expect(inputUsersIdentifierError.innerText).eql(' Identifiant incorrect\n\n')

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test("J'ai un mot de passe invalide, je vois un messages d'erreur et je reste sur la page /connection", async t => {

  await t
  .typeText(inputUsersIdentifier, offererUser.email)
  .typeText(inputUsersPassword, 'Pa$$word')
  .wait(1000)
  .click(signInButton)
  .wait(1000)

  .expect(inputUsersPasswordError.innerText).eql(' Mot de passe incorrect\n\n')

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test
  .page `${ROOT_PATH+'offres'}`
  ("Lorsque j'accède à une page sans être connecté·e, je suis redirigé·e vers la page connexion", async t => {
    await t
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/connexion')
    await t.expect(errorMessages.innerText).eql('Authentification nécessaire')
})
