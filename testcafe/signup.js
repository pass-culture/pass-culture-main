import { Selector } from 'testcafe'

import { BROWSER_ROOT_URL } from './helpers/config'
import { offererUser } from './helpers/users'

const publicNameInput = Selector('#sign-up-publicName')
const emailInput = Selector('#sign-up-email')
const passwordInput = Selector('#sign-up-password')
const contactOkInput = Selector('#sign-up-contact_ok')
const signUpButton = Selector('button.button.is-primary')
const signInButton = Selector('.is-secondary')
const sirenInput = Selector('#sign-up-siren')
const newsletterOkInput = Selector('#sign-up-newsletter_ok')

fixture `SignupPage | Création d'un compte utilisateur·ice`
    .page `${BROWSER_ROOT_URL+'inscription'}`


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

test("Lorsqu'un·e utilisateur·ice est créé, iel est redirigé·e vers la page /structures", async t => {
    await t
      .typeText(publicNameInput, offererUser.publicName)
      .typeText(emailInput, offererUser.email)
      .typeText(passwordInput, offererUser.password)
      .typeText(sirenInput, offererUser.siren)
      .click(contactOkInput)
      .click(newsletterOkInput)
      .wait(1000)

    await t
      .click(signUpButton)
      .wait(1000)

    const location = await t.eval(() => window.location)
    await t.expect(location.pathname).eql('/structures')
  })
