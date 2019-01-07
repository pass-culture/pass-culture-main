import { Role, Selector } from 'testcafe'

import { ROOT_PATH } from '../../src/utils/config'
import { youngUser } from './users'

const signInButton = Selector('#signin-submit-button')

export const youngUserRole = Role(`${ROOT_PATH}connexion`, async t => {
  await t
    .typeText('#user-identifier', youngUser.email)
    .wait(100)
    .typeText('#user-password', youngUser.password)
    .wait(100)
    .click(signInButton)
    .wait(1000)
})

export default youngUserRole
