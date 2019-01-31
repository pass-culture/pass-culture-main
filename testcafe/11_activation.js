import { Selector } from 'testcafe'

// testcafe chrome ./testcafe/11_activation.js
import { hasBookedSomeUser, hasSignedUpUser } from './helpers/users'
import { ROOT_PATH } from '../src/utils/config'

const activationEmailSpan = Selector('#activation-email')
const cguInput = Selector("input[name='cguCheckBox']")
const errorSpan = Selector('span.pc-error-message').withText(
  'Votre lien de changement de mot de passe est invalide.'
)
const newPasswordInput = Selector('#activation-newPassword')
const newPasswordConfirm = Selector('#activation-newPasswordConfirm')
const submitButton = Selector("button[type='submit']")

fixture("11 ActivationPage A | succès de l'activation")

test('Je suis redirigé·e vers découverte', async t => {
  // given
  const { email, password, resetPasswordToken } = hasSignedUpUser
  const url = `${ROOT_PATH}activation/${resetPasswordToken}?email=${email}`

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

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).match(/\/decouverte\/tuto\/([A-Z0-9]*)$/)
})

fixture("11 ActivationPage B | erreurs avec l'activation")

test('Sans token, je suis redirigé·e vers /activation/error', async t => {
  // when
  await t.navigateTo(`${ROOT_PATH}activation`)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/activation/error')
})

test('Sans email en query, je suis redirigé·e vers /activation/error', async t => {
  // when
  await t.navigateTo(`${ROOT_PATH}activation/fake`)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/activation/error')
})

test("Avec un email déjà activé, j'ai un message d'erreur", async t => {
  // given
  const { email, password } = hasBookedSomeUser

  // when
  await t.navigateTo(`${ROOT_PATH}activation/fake?email=${email}`)

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
