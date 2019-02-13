import { Selector } from 'testcafe'

import getPageUrl from './helpers/getPageUrl'
import { ROOT_PATH } from '../src/utils/config'
import { hasSignedUpUser93 } from './helpers/users'

const activationEmailSpan = Selector('#activation-email')
const cguInput = Selector("input[name='cguCheckBox']")
const errorSpan = Selector('span.pc-error-message').withText(
  'Votre lien de changement de mot de passe est invalide.'
)
const newPasswordInput = Selector('#activation-newPassword')
const newPasswordConfirm = Selector('#activation-newPasswordConfirm')
const submitButton = Selector("button[type='submit']")

const baseURL = `${ROOT_PATH}activation`

fixture(`01 ActivationPage A | succès de l'activation`)

test('Je suis redirigé·e vers découverte', async t => {
  // given
  const { email, password, resetPasswordToken } = hasSignedUpUser93
  const url = `${baseURL}/${resetPasswordToken}?email=${email}`

  // when
  await t.navigateTo(url)

  // then
  await t.expect(activationEmailSpan.innerText).eql(email)

  // when
  await t
    .typeText(newPasswordInput, password)
    .typeText(newPasswordConfirm, password)
    .click(cguInput)
    .click(submitButton)
    .wait(10000)
    .expect(getPageUrl())
    .match(/\/decouverte\/tuto\/([A-Z0-9]*)$/)
})

fixture("01 ActivationPage B | erreurs avec l'activation")

test('Sans token, je suis redirigé·e vers /activation/error', async t => {
  await t
    .navigateTo(`${baseURL}`)
    .expect(getPageUrl())
    .eql(`${baseURL}/error`)
})

test('Sans email en query, je suis redirigé·e vers /activation/error', async t => {
  await t
    .navigateTo(`${baseURL}/missing_email`)
    .expect(getPageUrl())
    .eql(`${baseURL}/error`)
})

test("Avec un email déjà activé, j'ai un message d'erreur", async t => {
  // given
  const { email, password } = hasSignedUpUser93

  // when
  await t.navigateTo(`${baseURL}/is_activated?email=${email}`)

  // when
  await t
    .typeText(newPasswordInput, password)
    .typeText(newPasswordConfirm, password)
    .click(cguInput)
    .click(submitButton)
    .wait(1000)

  // then
  await t
    .expect(errorSpan.visible)
    .ok()
    .expect(submitButton.hasAttribute('disabled'))
    .ok()
})
