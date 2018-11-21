import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { offererUser0 } from './helpers/users'

const inputUsersEmail = Selector('#user-email')
const forgotPasswordLink = Selector('#lostPasswordLink')
const sendTokenButton = Selector('#sendTokenByMail')
const changePasswordButton = Selector('#changePassword')
const passwordInput = Selector('#user-newPassword')
const pageH1 = Selector('h1')
const errorsDiv = Selector('.errors')

fixture`08_01 Lost Password link | La page de connexion propose un lien pour changer de mot de passe`
  .page`${ROOT_PATH + 'connexion'}`

test('Je peux cliquer sur lien mot de passe oublié', async t => {
  await t.click(forgotPasswordLink)
  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/mot-de-passe-perdu')
    .expect(pageH1.innerText)
    .eql('Mot de passe égaré ?')

  await t.typeText(inputUsersEmail, offererUser0.email).click(sendTokenButton)

  location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/mot-de-passe-perdu')
    .expect(location.search)
    .eql('?envoye=1')
    .expect(pageH1.innerText)
    .eql('Merci !')
})

fixture`08_03 Lost Password form | La page de changement de mot de passe vérifie le token`
  .page`${ROOT_PATH + 'mot-de-passe-perdu?token=ABCD'}`

test('Je ne peux pas changer mon mot de passe de sans token valide', async t => {
  await t.expect(pageH1.innerText).eql('Créer un nouveau mot de passe')
  await t.typeText(passwordInput, 'ABCD').click(changePasswordButton)

  await t.expect(errorsDiv.innerText).notEql('')
})
