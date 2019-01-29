import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { FUTURE_USER_WITH_UNREGISTERED_OFFERER } from './helpers/users'

const inputUsersEmail = Selector('#user-email')
const forgotPasswordLink = Selector('#lostPasswordLink')
const sendTokenButton = Selector('#sendTokenByMail')
const changePasswordButton = Selector('#changePassword')
const passwordInput = Selector('#user-newPassword')
const pageH1 = Selector('h1')
const errorsDiv = Selector('.errors')

fixture`LostPasswordPage A | La page de connexion propose un lien pour changer de mot de passe`
  .page`${ROOT_PATH + 'connexion'}`

test('Je peux cliquer sur lien mot de passe oublié', async t => {
  await t.click(forgotPasswordLink)
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/mot-de-passe-perdu')
    .expect(pageH1.innerText)
    .eql('Mot de passe égaré ?')

  await t
    .typeText(inputUsersEmail, FUTURE_USER_WITH_UNREGISTERED_OFFERER.email)
    .click(sendTokenButton)

  location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/mot-de-passe-perdu')
    .expect(location.search)
    .eql('?envoye=1')
    .expect(pageH1.innerText)
    .eql('Merci !')
})

fixture`LostPasswordPage B | La page de changement de mot de passe vérifie le token`
  .page`${ROOT_PATH + 'mot-de-passe-perdu?token=ABCD'}`

test('Je ne peux pas changer mon mot de passe de sans token valide', async t => {
  await t.expect(pageH1.innerText).eql('Créer un nouveau mot de passe')
  await t.typeText(passwordInput, 'ABCD').click(changePasswordButton)

  await t.expect(errorsDiv.innerText).notEql('')
})
