import { Selector } from 'testcafe'

import { fetchSandbox } from './helpers/sandboxes'
import { ROOT_PATH } from '../src/utils/config'

const inputUserIdentifier = Selector('#user-identifier')
const inputUserPassword = Selector('#user-password')
const signInButton = Selector('button').withText('Se connecter')

fixture('Suite à la création de mon compte').page(`${ROOT_PATH + 'connexion'}`)

test("Je me connecte avec un compte valide, sans offres, et je suis redirigé·e vers la page 'structures'", async t => {
  // given
  const { user } = await fetchSandbox('pro_02_signin', 'get_existing_pro_validated_user')
  const { email, password } = user

  // when
  await t
    .typeText(inputUserIdentifier, email)
    .typeText(inputUserPassword, password)
    .click(signInButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/structures')
})

test("Je me connecte avec un compte valide, avec des offres existantes, et je suis redirigé·e vers la page 'offres'", async t => {
  // given
  const { user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )
  const { email, password } = user

  // when
  await t
    .typeText(inputUserIdentifier, email)
    .typeText(inputUserPassword, password)
    .click(signInButton)

  // then
  const location = await t.eval(() => window.location)
  await t.expect(location.pathname).eql('/offres')
})
