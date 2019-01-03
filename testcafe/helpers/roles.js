import { Role, Selector } from 'testcafe'

import { ROOT_PATH } from '../../src/utils/config'
import { youngUser } from './users'

const signInButton = Selector('button').withText('Connexion')

export const youngUserRole = Role(
  `${ROOT_PATH}connexion`,
  async t => {
    await t
      .typeText('#user-identifier', youngUser.email)
      .typeText('#user-password', youngUser.password)
      .wait(500)
      .click(signInButton)
      .wait(500)
  },
  {
    preserveUrl: true,
  }
)

export default youngUserRole
