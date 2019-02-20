import { ClientFunction, Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'

const getPageUrl = ClientFunction(() => window.location.href.toString())

const userContactOk = Selector('#user-contact_ok')
const userEmail = Selector('#user-email')
const userEmailError = Selector('#user-email-error')
const userPassword = Selector('#user-password')
const userPasswordError = Selector('#user-password-error')
const userPublicName = Selector('#user-publicName')
const signInButton = Selector('.is-secondary')
const signUpButton = Selector('button.button.is-primary')

const FUTURE_USER = {
  email: 'pctest.jeune93.new@btmx.fr',
  password: 'pctest.Jeune93.new',
  publicName: 'PC Test Jeune93 NEW',
}

fixture
  .skip('01_01 SignupPage Component | Je crée un compte utilisatrice')
  .page(`${ROOT_PATH}inscription`)

test("Je peux cliquer sur lien pour me connecter si j'ai déja un compte", async t => {
  // when
  await t.click(signInButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test("Lorsque l'un des champs obligatoire est manquant, le bouton créer est desactivé", async t => {
  // when
  await t.typeText(userEmail, FUTURE_USER.email).wait(500)

  // then
  await t
    .expect(signUpButton.innerText)
    .eql('Créer')
    .expect(signUpButton.hasAttribute('disabled'))
    .ok()
})

test('Je crée un compte et je suis redirigé·e vers la page /découverte', async t => {
  // given
  await t
    .typeText(userPublicName, FUTURE_USER.publicName)
    .typeText(userEmail, FUTURE_USER.email)
    .typeText(userPassword, FUTURE_USER.password)
  await t.click(userContactOk).wait(1000)

  // when
  await t.click(signUpButton).wait(500)

  // then
  await t.expect(getPageUrl()).contains('/decouverte', { timeout: 3000 })
})

fixture
  .skip(
    "01_02 SignupPage | Création d'un compte utilisateur | Messages d'erreur lorsque les champs ne sont pas correctement remplis"
  )
  .page(`${ROOT_PATH}inscription`)

test('E-mail déjà présent dans la base et mot de passe invalide', async t => {
  // given
  await t
    .typeText(userPublicName, FUTURE_USER.publicName)
    .typeText(userEmail, FUTURE_USER.email)
    .typeText(userPassword, 'pas')
    .wait(1000)
    .click(userContactOk)
    .wait(1000)

  // when
  await t.click(signUpButton).wait(1000)

  // then
  await t
    .expect(userPasswordError.innerText)
    .eql(
      '\nLe mot de passe doit faire au moins 12 caractères et contenir à minima 1 majuscule, 1 minuscule, 1 chiffre et 1 caractère spécial parmi _-&?~#|^@=+.$,<>%*!:;\n\n'
    )

  // when
  await t
    .typeText(userPassword, 'RTit.uioRZU.90')
    .click(signUpButton)
    .wait(2000)

  // then
  await t
    .expect(userEmailError.innerText)
    .eql('\nUn compte lié à cet email existe déjà\n\n')
})

test('E-mail non autorisé', async t => {
  // given
  await t
    .typeText(userPublicName, FUTURE_USER.publicName)
    .typeText(userEmail, 'test@test.fr')
    .typeText(userPassword, FUTURE_USER.password)
    .wait(1000)
    .click(userContactOk)
    .wait(1000)

  // when
  await t.click(signUpButton).wait(1000)

  // then
  await t
    .expect(userEmailError.innerText)
    .eql("\nAdresse non autorisée pour l'expérimentation\n\n")
})
