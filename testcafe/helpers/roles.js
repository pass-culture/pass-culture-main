import { Role, Selector } from 'testcafe'

import { ROOT_PATH } from '../../src/utils/config'

const signInButton = Selector('#signin-submit-button')

export const signinAs = user => async t => {
  await t
    .typeText('#user-identifier', user.email)
    .wait(100)
    .typeText('#user-password', user.password)
    .wait(100)
    .click(signInButton)
    .wait(1000)
}

export const createUserRole = user =>
  Role(`${ROOT_PATH}connexion`, signinAs(user), { preserveUrl: true })
