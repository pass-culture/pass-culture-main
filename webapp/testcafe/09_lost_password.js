import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import getPageUrl from './helpers/getPageUrl'
import { fetchSandbox } from './helpers/sandboxes'

fixture('En étant déconnecté de l’application,')

test('je clique sur "mot de passe oublié", je remplis le formulaire avec une adresse e-mail et je suis redirigé·e vers la page de confirmation', async t => {
  const {
    user: { email },
  } = await fetchSandbox('webapp_09_lost_password', 'get_webapp_user_with_not_validated_password')
  const forgotPasswordLink = Selector('.lf-lost-password')
  const inputUserEmail = Selector('#email')
  const sendTokenButton = Selector('footer > button')
  const pageH2Title = Selector('.logout-form-title')

  await t
    .navigateTo(`${ROOT_PATH}connexion`)
    .click(forgotPasswordLink)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}mot-de-passe-perdu`)
    .expect(pageH2Title.innerText)
    .eql('Renseigne ton adresse e-mail pour réinitialiser ton mot de passe.')
    .typeText(inputUserEmail, email)
    .click(sendTokenButton)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}mot-de-passe-perdu/succes`)
})

test('je clique sur le lien reçu par e-mail, je saisis mon nouveau mot de passe, et je suis redirigé·e vers la page de confirmation', async t => {
  const {
    user: { resetPasswordToken },
  } = await fetchSandbox('webapp_09_lost_password', 'get_webapp_user_with_not_validated_password')
  const userNewPasswordInput = Selector('#newPassword')
  const userNewPasswordConfirmInput = Selector('#newPasswordConfirm')
  const submitNewPasswordButton = Selector("button[type='submit']")

  await t
    .navigateTo(`${ROOT_PATH}mot-de-passe-perdu?token=${resetPasswordToken}`)
    .typeText(userNewPasswordInput, 'user@AZERTY123')
    .typeText(userNewPasswordConfirmInput, 'newuser@AZERTY123')
    .expect(submitNewPasswordButton.hasAttribute('disabled'))
    .ok()
    .typeText(userNewPasswordConfirmInput, 'user@AZERTY123', { replace: true })
    .click(submitNewPasswordButton)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}mot-de-passe-perdu/succes?token=${resetPasswordToken}`)
})
