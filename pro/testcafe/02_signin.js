import { Selector } from 'testcafe'

import { ROOT_PATH } from '../src/utils/config'

import { getPathname } from './helpers/location'
import { HOME_URL } from './helpers/navigations'
import { fetchSandbox } from './helpers/sandboxes'

const inputUserIdentifier = Selector('input[name="identifier"]')
const inputUserPassword = Selector('input[name="password"]')
const signInButton = Selector('button').withText('Se connecter')

fixture('Suite à la création de mon compte,')

test("je me connecte avec un compte valide, et je suis redirigé·e vers la page d'accueil", async t => {
  const { user } = await fetchSandbox(
    'pro_02_signin',
    'get_existing_pro_validated_user_without_offer'
  )

  await t
    .navigateTo(`${ROOT_PATH}connexion`)
    .typeText(inputUserIdentifier, user.email, { paste: true })
    .typeText(inputUserPassword, user.password, { paste: true })
    .click(signInButton)
    .expect(getPathname())
    .eql(HOME_URL)
})
