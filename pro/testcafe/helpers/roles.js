import { Role, Selector } from 'testcafe'

import { ROOT_PATH } from '../../src/utils/config'

const signInButton = Selector('button').withText('Se connecter')

export const signinAs = user => async t => {
  await t
    .typeText('input[name="email"]', user.email, { paste: true })
    .typeText('input[name="password"]', user.password, { paste: true })
    .click(signInButton)
}

export const createUserRole = user =>
  Role(`${ROOT_PATH}connexion`, signinAs(user), { preserveUrl: true })
