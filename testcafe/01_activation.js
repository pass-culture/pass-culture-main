import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import getPageUrl from './helpers/getPageUrl'
import { fetchSandbox } from './helpers/sandboxes'

fixture('Activation d’un compte utilisateur·trice,')

test('lorsque je clique sur le lien reçu par e-mail et que je saisis mon premier mot de passe, je suis redirigé vers le Typeform', async t => {
  const { user } = await fetchSandbox(
    'webapp_01_activation',
    'get_existing_webapp_not_validated_user'
  )
  const { email, password, resetPasswordToken } = user
  const activationEmailSpan = Selector('.activation-email')
  const cguInput = Selector("input[name='cguCheckBox']")
  const newPasswordInput = Selector('#activation-newPassword')
  const newPasswordConfirm = Selector('#activation-newPasswordConfirm')
  const submitButton = Selector("button[type='submit']")

  await t
    .navigateTo(`${ROOT_PATH}activation/${resetPasswordToken}?email=${email}`)
    .expect(activationEmailSpan.innerText)
    .eql(email)
    .typeText(newPasswordInput, password)
    .typeText(newPasswordConfirm, password)
    .click(cguInput)
    .click(submitButton)
    .expect(getPageUrl())
    .eql(`${ROOT_PATH}typeform`)
})
