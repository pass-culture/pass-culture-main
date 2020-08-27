import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { getPathname, getUrlParams } from './helpers/location'
import { fetchSandbox } from './helpers/sandboxes'

const inputUserEmail = Selector('#user-email')
const forgotPasswordLink = Selector('#lostPasswordLink')
const sendTokenButton = Selector('#sendTokenByMail')
const pageH1 = Selector('h1')
const submitNewPasswordButton = Selector('#changePassword')
const userNewPasswordInput = Selector('#user-newPassword')

fixture('En étant déconnecté de l’application').page(`${ROOT_PATH}connexion`)

test('je clique sur "mot de passe égaré", je remplis le formulaire avec une adresse e-mail et je suis redirigé·e vers la page de confirmation', async t => {
  // given
  const {
    user: { email },
  } = await fetchSandbox('pro_11_lost_password', 'get_pro_validated_no_reset_password_token_user')
  await t
    .click(forgotPasswordLink)
    .expect(getPathname())
    .eql('/mot-de-passe-perdu')
    .expect(pageH1.innerText)
    .eql('Mot de passe égaré ?')

  // when
  await t.typeText(inputUserEmail, email).click(sendTokenButton)

  // then
  await t
    .expect(getPathname())
    .eql('/mot-de-passe-perdu')
    .expect(getUrlParams())
    .eql('?envoye=1')
    .expect(pageH1.innerText)
    .eql('Merci !')
})

test('je clique sur le lien reçu par e-mail, je saisis mon nouveau mot de passe, et je suis redirigé·e vers la page de confirmation', async t => {
  // given
  const {
    user: { resetPasswordToken },
  } = await fetchSandbox('pro_11_lost_password', 'get_pro_validated_with_reset_password_token_user')
  await t.navigateTo(`/mot-de-passe-perdu?token=${resetPasswordToken}`)

  // when
  await t.typeText(userNewPasswordInput, 'user@AZERTY123').click(submitNewPasswordButton)

  // then
  await t
    .expect(getPathname())
    .eql('/mot-de-passe-perdu')
    .expect(getUrlParams())
    .eql('?change=1')
})
