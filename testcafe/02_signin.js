import { Selector } from 'testcafe'
import getPageUrl from './helpers/getPageUrl'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const userId = '#user-identifier'
const passId = '#user-password'
const errorClass = '.pc-error-message'
const userPassword = Selector(passId)
const userIdentifier = Selector(userId)
const passwordError = Selector(`${passId}-error`).find(errorClass)
const identifierErrors = Selector(`${userId}-error`).find(errorClass)
const signInButton = Selector('#signin-submit-button')

fixture("02_01 SignIn | J'ai un compte et je me connecte")
  .page(`${ROOT_PATH}connexion`)
  .beforeEach(async t => {
    t.ctx.sandbox = await fetchSandbox(
      'webapp_02_signin',
      'get_existing_webapp_validated_user_with_has_filled_cultural_survey'
    )
  })

test("Lorsque l'un des deux champs est manquant, le bouton connexion est désactivé", async t => {
  // given
  const { user } = t.ctx.sandbox
  const { email } = user

  // when
  await t.typeText(
    userIdentifier,
    email,
    // https://github.com/DevExpress/testcafe/issues/3865
    { paste: true }
  )

  // then
  await t.expect(signInButton.hasAttribute('disabled')).ok()
})

test("J'ai un compte valide, je suis redirigé·e vers la page /decouverte sans erreurs", async t => {
  // given
  const { user } = t.ctx.sandbox
  const { email, password } = user
  await t
    .typeText(
      userIdentifier,
      email,
      // https://github.com/DevExpress/testcafe/issues/3865
      { paste: true }
    )
    .typeText(userPassword, password)

  // when
  await t.click(signInButton).wait(1000)

  // then
  await t.expect(identifierErrors.count).eql(0)
  await t.expect(getPageUrl()).contains('/decouverte')
})

test("J'ai un identifiant invalide, je vois un message d'erreur et je reste sur la page /connexion", async t => {
  // given
  const { user } = t.ctx.sandbox
  const { password } = user
  await t
    .typeText(
      userIdentifier,
      'wrongEmail@test.com',
      // https://github.com/DevExpress/testcafe/issues/3865
      { paste: true }
    )
    .typeText(userPassword, password)

  // when
  await t.click(signInButton).wait(1000)

  // then
  const location = await t.eval(() => window.location)
  await t
    .expect(identifierErrors.count)
    .gte(1)
    .expect(identifierErrors.nth(0).innerText)
    .eql('Identifiant incorrect')
    .expect(location.pathname)
    .eql('/connexion')
})

test("J'ai un mot de passe vide, avant envoi à l'API, je vois un message d'erreur et je reste sur la page /connexion", async t => {
  // given
  const { user } = t.ctx.sandbox
  const { email, password } = user

  // when
  await t
    .typeText(userPassword, password)
    .selectText(userPassword)
    .pressKey('delete')
    .typeText(
      userIdentifier,
      email,
      // https://github.com/DevExpress/testcafe/issues/3865
      { paste: true }
    )
    .wait(1000)

  // then
  const location = await t.eval(() => window.location)
  await t
    .expect(passwordError.count)
    .gte(1)
    .expect(passwordError.nth(0).innerText)
    .eql('Ce champ est requis.')
    .expect(location.pathname)
    .eql('/connexion')
})

test("J'ai un mot de passe invalide, je vois un message d'erreur et je reste sur la page /connexion", async t => {
  // given
  const { user } = t.ctx.sandbox
  const { email } = user

  // when
  await t
    .typeText(
      userIdentifier,
      email,
      // https://github.com/DevExpress/testcafe/issues/3865
      { paste: true }
    )
    .typeText(userPassword, 'Pa$$word4242')
    .click(signInButton)
    .wait(1000)

  // then
  const location = await t.eval(() => window.location)
  await t
    .expect(passwordError.count)
    .gte(1)
    .expect(passwordError.nth(0).innerText)
    .eql('Mot de passe incorrect')
    .expect(location.pathname)
    .eql('/connexion')
})
