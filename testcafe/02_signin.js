import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'
import { getPathname } from './helpers/location'
import { fetchSandbox } from './helpers/sandboxes'

const inputUserIdentifier = Selector('input[name="identifier"]')
const inputUserPassword = Selector('input[name="password"]')
const signInButton = Selector('button').withText('Se connecter')

fixture('Suite à la création de mon compte,')

test('je me connecte avec un compte valide, sans offres, et je suis redirigé·e vers la page "structures"', async t => {
  const { user } = await fetchSandbox('pro_02_signin', 'get_existing_pro_validated_user')

  await t
    .navigateTo(`${ROOT_PATH}connexion`)
    .typeText(inputUserIdentifier, user.email)
    .typeText(inputUserPassword, user.password)
    .click(signInButton)
    .expect(getPathname())
    .eql('/structures')
})

test('je me connecte avec un compte valide, avec des offres existantes, et je suis redirigé·e vers la page "offres"', async t => {
  const { user } = await fetchSandbox(
    'pro_07_offer',
    'get_existing_pro_validated_user_with_validated_offerer_validated_user_offerer_with_physical_venue'
  )

  await t
    .navigateTo(`${ROOT_PATH}connexion`)
    .typeText(inputUserIdentifier, user.email)
    .typeText(inputUserPassword, user.password)
    .click(signInButton)
    .expect(getPathname())
    .eql('/offres')
})
