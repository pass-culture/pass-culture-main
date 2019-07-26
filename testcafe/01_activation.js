import { Selector } from 'testcafe'

import getPageUrl from './helpers/getPageUrl'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const activationEmailSpan = Selector('#activation-email')
const cguInput = Selector("input[name='cguCheckBox']")
const newPasswordInput = Selector('#activation-newPassword')
const newPasswordConfirm = Selector('#activation-newPasswordConfirm')
const submitButton = Selector("button[type='submit']")

const baseURL = `${ROOT_PATH}activation`

fixture(`Activation d'un compte utilisateur·trice`)

test('Lorsque je clique sur le lien reçu par mail et que je saisis mon premier mot de passe, je suis redirigé vers le TypeForm', async t => {
  // given
  const { user } = await fetchSandbox(
    'webapp_01_activation',
    'get_existing_webapp_not_validated_user'
  )
  const { email, password, resetPasswordToken } = user
  const url = `${baseURL}/${resetPasswordToken}?email=${email}`

  // when
  await t
    .navigateTo(url)
    .expect(activationEmailSpan.innerText).eql(email)
    .typeText(newPasswordInput, password)
    .typeText(newPasswordConfirm, password)
    .click(cguInput)
    .click(submitButton)

  // then
  await t.expect(getPageUrl()).eql(`${ROOT_PATH}typeform`)
})
