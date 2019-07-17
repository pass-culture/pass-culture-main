import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const inputUserEmail = Selector('#user-email')
const forgotPasswordLink = Selector('#lostPasswordLink')
const sendTokenButton = Selector('#sendTokenByMail')
const pageH1 = Selector('h1')
const submitNewPasswordButton = Selector('#changePassword')
const userNewPasswordInput = Selector('#user-newPassword')

fixture("En étant déconnecté de l'application").page(`${ROOT_PATH + 'connexion'}`)

test('Je clique sur "mot de passe égaré", je remplis le formulaire avec une adresse email et je suis redirigé·e vers la page de confirmation', async t => {
  // given
  const { user } = await fetchSandbox(
    'pro_11_lost_password',
    'get_pro_validated_no_reset_password_token_user'
  )
  const { email } = user

  // when
  await t.click(forgotPasswordLink)

  let location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/mot-de-passe-perdu')
    .expect(pageH1.innerText)
    .eql('Mot de passe égaré ?')

  // when
  await t.typeText(inputUserEmail, email).click(sendTokenButton)

  // then
  location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/mot-de-passe-perdu')
    .expect(location.search)
    .eql('?envoye=1')
    .expect(pageH1.innerText)
    .eql('Merci !')
})

test('Je clique sur le lien reçu par email, je saisis mon nouveau mot de passe, et je suis redirigé·e vers la page de confirmation', async t => {
  // given
  const { user } = await fetchSandbox(
    'pro_11_lost_password',
    'get_pro_validated_with_reset_password_token_user'
  )
  const { resetPasswordToken } = user

  // when
  await t.navigateTo('/mot-de-passe-perdu?token=' + resetPasswordToken)

  await t.typeText(userNewPasswordInput, 'user@AZERTY123').click(submitNewPasswordButton)

  // then
  const location = await t.eval(() => window.location)
  await t
    .expect(location.pathname)
    .eql('/mot-de-passe-perdu')
    .expect(location.search)
    .eql('?change=1')
})
