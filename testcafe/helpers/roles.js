import { ClientFunction, Role, Selector } from 'testcafe'

import { ROOT_PATH } from '../../src/utils/config'
import youngUser from './users'

const getPageUrl = ClientFunction(() => window.location.href.toString())
const signInButton = Selector('button').withText('Connexion')

const regularUser = Role(
  `${ROOT_PATH}connexion`,
  async t => {
    await t
      .typeText('#user-identifier', youngUser.email)
      .typeText('#user-password', youngUser.password)
      .wait(500)
      .click(signInButton)
      .wait(500)
    await t.expect(getPageUrl()).contains('/decouverte', { timeout: 1000 })
  },
  {
    preserveUrl: true,
  }
)

export default regularUser
