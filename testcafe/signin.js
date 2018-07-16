import { Selector } from 'testcafe'

import { BROWSER_ROOT_URL } from './helpers/config'

const inputUsersIdentifier = Selector('#input_users_identifier')
const inputUsersPassword = Selector('#input_users_password')
const inputUsersIdentifierError = Selector('#input_users_identifier-error')
const inputUsersPasswordError = Selector('#input_users_password-error')
const signInButton  = Selector('button.button.is-primary') //connexion
const signUpButton  = Selector('.is-secondary') // inscription
const errorMessages  = Selector('.errors') // inscription


fixture `SignInPage | Se connecter en tant qu'utilisateur·ice`
    .page `${BROWSER_ROOT_URL+'connexion'}`

test("Je peux cliquer sur lien Créer un compte", async t => {
  await t
  .click(signUpButton)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription')
})

test("Lorsque l'un des deux champs est manquant, le bouton connexion est desactivé", async t => {
  await t
    .typeText(inputUsersIdentifier, 'email@email.test')
    .wait(1000)
  await t.expect(signInButton.hasAttribute('disabled')).ok()
})

test("J'ai un compte valide, je suis redirigé·e vers la page /offres sans erreurs", async t => {

  await t
  .typeText(inputUsersIdentifier, 'pctest.cafe@btmx.fr')
  .typeText(inputUsersPassword, 'pctestcafe')
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
  .typeText(inputUsersIdentifier, 'pctest.cafe@btmx.fr')
  .typeText(inputUsersPassword, 'Pa$$word')
  .wait(1000)
  .click(signInButton)
  .wait(1000)

  .expect(inputUsersPasswordError.innerText).eql(' Mot de passe incorrect\n\n')

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test
  .page `${BROWSER_ROOT_URL+'offres'}`
  ("Lorsque j'accède à une page sans être connecté·e, je suis redirigé·e vers la page connexion", async t => {
    await t
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/connexion')
    await t.expect(errorMessages.innerText).eql('Authentification nécessaire')
})
