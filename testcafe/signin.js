import { Selector } from 'testcafe'

const inputUsersIdentifier = Selector('#input_users_identifier')
const inputUsersPassword = Selector('#input_users_password')
const inputUsersIdentifierError = Selector('#input_users_identifier-error')
const inputUsersPasswordError = Selector('#input_users_password-error')
const signInButton  = Selector('button') //connexion
const signUpButton  = Selector('.is-secondary') // inscription

fixture `SignupPage | Se connecter en tant qu'utilisateur`
    .page `http://localhost:3000/connexion`

test("Je peux cliquer sur lien /inscription", async t => {

  await t
  .click(signUpButton)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/inscription')
})

test("Lorsque l'un des deux champs est manquant, le bouton connexion est desactivé", async t => {
    await t
    .typeText(inputUsersIdentifier, 'email@email.test')
    .wait(1000)
    .expect(signInButton.hasAttribute('disabled')).ok()
})

test("J'ai un compte valide, je suis redirigé vers la page /decouverte sans erreurs", async t => {

  await t
  .typeText(inputUsersIdentifier, 'testcafe_user@btmx.fr')
  .typeText(inputUsersPassword, 'password1234')
  .wait(1000)
  .click(signInButton)
  .wait(1000)

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/decouverte/empty')
})


test("J'ai un compte Identifiant invalide, je vois un messages d'erreur et je reste sur la page /connection", async t => {

  await t
  .typeText(inputUsersIdentifier, 'email@email.test')
  .typeText(inputUsersPassword, 'Pa$$word')
  .wait(1000)
  .click(signInButton)
  .wait(1000)

  .expect(inputUsersIdentifierError.innerText).eql(' Identifiant incorrect\n')

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test("J'ai un mot de passe invalide, je vois un messages d'erreur et je reste sur la page /connection", async t => {

  await t
  .typeText(inputUsersIdentifier, 'testcafe_user@btmx.fr')
  .typeText(inputUsersPassword, 'Pa$$word')
  .wait(1000)
  .click(signInButton)
  .wait(1000)

  .expect(inputUsersPasswordError.innerText).eql(' Mot de passe incorrect\n')

  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})
