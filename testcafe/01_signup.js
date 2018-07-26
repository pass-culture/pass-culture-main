import { Selector, RequestLogger } from 'testcafe'

import { API_URL, ROOT_PATH } from '../src/utils/config'
import { offererUser } from './helpers/users'

const LOGGER_URL = API_URL + '/users'

const logger = RequestLogger(LOGGER_URL, {
  logResponseBody: true,
  stringifyResponseBody: true,
  logRequestBody: true,
  stringifyRequestBody: true
})

const contactOkInput = Selector('#sign-up-contact_ok')
const emailInput = Selector('#sign-up-email')
const passwordInput = Selector('#sign-up-password')
const newsletterOkInput = Selector('#sign-up-newsletter_ok')
const publicNameInput = Selector('#sign-up-publicName')
const signInButton = Selector('.is-secondary')
const signUpButton = Selector('button.button.is-primary')
const sirenInput = Selector('#sign-up-siren')

fixture `01_01 SignupPage |  Component | Je crée un compte utilisateur·ice`
    .page `${ROOT_PATH+'inscription'}`

test("Je peux cliquer sur lien pour me connecter si j'ai déja un compte", async t => {

  await t
  .click(signInButton)
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/connexion')
})

test("Lorsque l'un des champs obligatoire est manquant, le bouton créer est desactivé", async t => {
    await t
    .typeText(emailInput, 'email@email.test')
    .wait(500)
    await t.expect(signUpButton.innerText).eql('Créer')
    await t.expect(signUpButton.hasAttribute('disabled')).ok()
})

test
.requestHooks(logger)
("Je créé un compte, je suis redirigé·e vers la page /structures", async t => {
    await t
      .typeText(publicNameInput, offererUser.publicName)
      .typeText(emailInput, offererUser.email)
      .typeText(passwordInput, offererUser.password)
      .typeText(sirenInput, offererUser.siren)
      .wait(1000)
      .click(contactOkInput)
      .click(newsletterOkInput)
      .wait(1000)
    await t
      .click(signUpButton)
      .wait(1000)
    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/structures')
  })
