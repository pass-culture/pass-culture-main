import { Role, Selector } from 'testcafe'

import { ROOT_PATH } from '../../src/utils/config'

const signInButton = Selector('#signin-submit-button')

export const signinAs = user => async t => {
  await t
    .typeText('input[name="identifier"]', user.email)
    .typeText('input[name="password"]', user.password)
    .click(signInButton)
}

export const createUserRole = user =>
  Role(`${ROOT_PATH}connexion`, signinAs(user), { preserveUrl: true })
