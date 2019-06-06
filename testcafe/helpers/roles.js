import { Role, Selector } from 'testcafe'

import getPageUrl from './getPageUrl'
import { ROOT_PATH } from '../../src/utils/config'

const signInButton = Selector('#signin-submit-button:enabled')

export const signinAs = user => async t => {
  await t
    .typeText(
      '#user-identifier',
      user.email,
      // https://github.com/DevExpress/testcafe/issues/3865
      { paste: true }
    )
    .typeText('#user-password', user.password)
    .click(signInButton)
  await t.expect(getPageUrl()).notContains('/connexion', { timeout: 10000 })
}

export const createUserRole = user =>
  Role(`${ROOT_PATH}connexion`, signinAs(user), { preserveUrl: true })
