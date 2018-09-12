import { Role } from 'testcafe'

import { ROOT_PATH } from '../../src/utils/config'
import youngUser from './users'

const regularUser = Role(
  `${ROOT_PATH}connexion`,
  async t => {
    await t
      .typeText('#user-identifier', youngUser.email)
      .typeText('#user-password', youngUser.password)
      .wait(500)
      .click('button')
      .wait(500)
  },
  {
    preserveUrl: true,
  }
)

export default regularUser
