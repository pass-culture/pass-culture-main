// $(yarn bin)/testcafe chrome:headless ./testcafe/01_activation.js
import { Selector } from 'testcafe'

import getPageUrl from './helpers/getPageUrl'
import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const activationEmailSpan = Selector('#activation-email')
const cguInput = Selector("input[name='cguCheckBox']")
const newPasswordInput = Selector('#activation-newPassword')
const newPasswordConfirm = Selector('#activation-newPasswordConfirm')
const mailToButton = Selector('#activation-error-contact-us')
const submitButton = Selector("button[type='submit']")

const baseURL = `${ROOT_PATH}activation`

fixture(`01_01 ActivationPage | succès de l'activation`)

test('Je suis redirigé·e vers découverte', async t => {
  // given
  const { user } = await fetchSandbox(
    'webapp_01_activation',
    'get_existing_webapp_not_validated_user'
  )
  const { email, password, resetPasswordToken } = user
  const url = `${baseURL}/${resetPasswordToken}?email=${email}`

  await t
    .navigateTo(url)
    .expect(activationEmailSpan.innerText)
    .eql(email, { timeout: 2000 })
    .typeText(newPasswordInput, password)
    .typeText(newPasswordConfirm, password)
    .click(cguInput)
    .click(submitButton)
    .wait(10000)
    .expect(getPageUrl())
    .match(/\/decouverte\/tuto\/([A-Z0-9]*)$/)
})

fixture("01_02 ActivationPage | erreurs avec l'activation")

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

test("Sur la page d'erreur d'activation je dois pouvoir cliquer sur le bouton contactez-nous", async t => {
  await t
    .navigateTo(`${baseURL}/error`)
    .expect(mailToButton.exists)
    .ok()
    .expect(mailToButton.textContent)
    .eql('Contactez-nous')
})

test('Avec un email déjà activé, je suis redirigé·e vers la page lien invalide', async t => {
  const { user } = await fetchSandbox(
    'webapp_01_activation',
    'get_existing_webapp_validated_user'
  )
  const { email } = user
  const tokenAlreadyUsed = 'BFYU73UV'

  await t
    .navigateTo(`${baseURL}/${tokenAlreadyUsed}?email=${email}`)
    .expect(getPageUrl())
    .eql(`${baseURL}/lien-invalide`)
})
